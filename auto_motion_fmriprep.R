# This script loads the fmriprep confound files, applies a machine learning classifier to 
# predict motion artifacts, and returns summaries by task, task and run, and trash volumes only. 
# It will also export new motion regressor files if writeRP = TRUE and plots if writePlots = TRUE.

# Inputs:
# * config.R = configuration file with user defined variables and paths

# Outputs:
# * study_summaryRun.csv = CSV file with summary by task and run
# * study_summaryTask.csv = CSV file with summary by task only
# * study_trashVols.csv = CSV file with trash volumes only
# * if writeRP = TRUE, rp_txt files will be written to outputDir/auto-motion-fmriprep/sub-[subject ID]
# * if writePlots = TRUE, plots for each subjects will be written to outputDir/auto-motion-fmriprep/sub-[subject ID]

#------------------------------------------------------
# load/install packages
#------------------------------------------------------
osuRepo = 'http://ftp.osuosl.org/pub/cran/'

if (!require(tidyverse)) {
  install.packages('tidyverse', repos = osuRepo)
}

if (!require(snakecase)) {
  install.packages('snakecase', repos = osuRepo)
}

if (!require(caret)) {
  install.packages('caret', repos = osuRepo)
}

if (!require(randomForest)) {
  install.packages('randomForest', repos = osuRepo)
}

#------------------------------------------------------
# source the config file
#------------------------------------------------------
source('config.R')

#------------------------------------------------------
# define output path
#------------------------------------------------------
outputDir = file.path(outputDir, "auto-motion-fmriprep")

#------------------------------------------------------
# load confound files
#------------------------------------------------------
message('--------Loading confound files--------')

dataset = data.frame()
columnNames = c("subjectID", "wave", "task", "run", "volume", "CSF", "WhiteMatter", 
                "GlobalSignal", "stdDVARS", "non.stdDVARS", "vx.wisestdDVARS", 
                "FramewiseDisplacement", "tCompCor00", "tCompCor01", "tCompCor02", 
                "tCompCor03", "tCompCor04", "tCompCor05", "aCompCor00", "aCompCor01", 
                "aCompCor02", "aCompCor03", "aCompCor04", "aCompCor05", "Cosine00", 
                "X", "Y", "Z", "RotX", "RotY", "RotZ")

fileRegex = '.*func/sub-(.*)_ses-(.*)_task-(.*)_run-(.*)_desc-.*.tsv'
fileVars = c('subjectID', 'wave', 'task', 'run')

if (gsub("\\.", "", version) <= 118) {
  fileList = list.files(confoundDir, pattern = 'bold_confounds.tsv', recursive = TRUE)
  
  for (file in fileList) {
    tmp = tryCatch(read_tsv(file.path(confoundDir, file)) %>% 
                     mutate(file = ifelse(!grepl("desc", file), gsub("bold", "desc-bold", file), file),
                            file = ifelse(!grepl("ses", file), gsub("task", "ses-1_task", file), file),
                            file = ifelse(!grepl("run", file), gsub("desc", "run-1_desc", file), file)) %>%
                     extract(file, fileVars,
                             fileRegex) %>%
                     mutate(wave = str_extract(wave, "[[:digit:]]+"),
                            run = str_extract(run, "[[:digit:]]+"),
                            wave = as.integer(wave),
                            run = as.integer(run),
                            stdDVARS = as.numeric(ifelse(stdDVARS %in% "n/a", 0, stdDVARS)),
                            `non-stdDVARS` = as.numeric(ifelse(`non-stdDVARS` %in% "n/a", 0, `non-stdDVARS`)),
                            `vx-wisestdDVARS` = as.numeric(ifelse(`vx-wisestdDVARS` %in% "n/a", 0, `vx-wisestdDVARS`)),
                            FramewiseDisplacement = as.numeric(ifelse(FramewiseDisplacement %in% "n/a", 0, FramewiseDisplacement)),
                            volume = row_number()) %>%
                     select(subjectID, wave, task, run, volume, everything()), error = function(e) message(file))

    # add missing columns and select subset classifier columns
    missingColumns = setdiff(columnNames, names(tmp))
    tmp[missingColumns] = 0 
    
    tmp = tmp  %>%
      select(subjectID, wave, task, run, volume, CSF, WhiteMatter, 
             GlobalSignal, stdDVARS, non.stdDVARS, vx.wisestdDVARS, 
             FramewiseDisplacement, tCompCor00, tCompCor01, tCompCor02, 
             tCompCor03, tCompCor04, tCompCor05, aCompCor00, aCompCor01, 
             aCompCor02, aCompCor03, aCompCor04, aCompCor05, Cosine00, 
             X, Y, Z, RotX, RotY, RotZ)
    
    if (length(tmp) > 0) {
      colnames(tmp) = gsub('-', '.', colnames(tmp))
      dataset = bind_rows(dataset, tmp)
      rm(tmp)
    }
  }
  
} else {
  
  fileList = list.files(confoundDir, pattern = '.*confounds.*.tsv', recursive = TRUE)

  for (file in fileList) {

      tmp = tryCatch(read_tsv(file.path(confoundDir, file)) %>%
                       setNames(snakecase::to_upper_camel_case(names(.))) %>%
                       setNames(gsub("AComp", "aComp", names(.))) %>%
                       setNames(gsub("TComp", "tComp", names(.))) %>%
                       setNames(gsub("Trans", "", names(.))) %>%
                       mutate(file = ifelse(!grepl("ses", file), gsub("task", "ses-1_task", file), file),
                              file = ifelse(!grepl("run", file), gsub("desc", "run-1_desc", file), file)) %>%
                       extract(file, fileVars,
                               fileRegex) %>%
                       rename("CSF" = Csf,
                              "stdDVARS" = StdDvars,
                              "non.stdDVARS" = Dvars) %>%
                       mutate(run = str_extract(run, "[[:digit:]]+"),
                              run = as.integer(run),
                              volume = row_number()) %>%
                       mutate_if(is.character, list(~ ifelse(. == "n/a", 0, .))) %>%
                       mutate_at(vars(contains("DVARS"), contains("Framewise")), as.numeric), error = function(e) message(file))
    
    # add missing columns and select subset classifier columns
    missingColumns = setdiff(columnNames, names(tmp))
    tmp[missingColumns] = 0 
    
    tmp = tmp  %>%
      select(subjectID, wave, task, run, volume, CSF, WhiteMatter, 
             GlobalSignal, stdDVARS, non.stdDVARS, vx.wisestdDVARS, 
             FramewiseDisplacement, tCompCor00, tCompCor01, tCompCor02, 
             tCompCor03, tCompCor04, tCompCor05, aCompCor00, aCompCor01, 
             aCompCor02, aCompCor03, aCompCor04, aCompCor05, Cosine00, 
             X, Y, Z, RotX, RotY, RotZ)
    
    if (length(tmp) > 0) {
      dataset = bind_rows(dataset, tmp)
      rm(tmp)
    }
  }  
}

#------------------------------------------------------
# apply classifier
#------------------------------------------------------
message('--------Applying classifier--------')

# load classifier
mlModel = readRDS('motion_classifier.rds')

# apply model
dataset$trash = predict(mlModel, dataset)

# recode trash as 1 or 0
dataset = dataset %>%
  mutate(trash = ifelse(trash == "yes", 1, 0),
         trash = ifelse(is.na(trash), 0, trash))

#------------------------------------------------------
# summarize data and write csv files
#------------------------------------------------------
message(sprintf('--------Writing summaries to %s--------', outputDir))

# summarize by task and run
summaryRun = dataset %>% 
  group_by(subjectID, wave, task, run) %>% 
  summarise(nVols = sum(trash, na.rm = T),
            percent = round((sum(trash, na.rm = T) / n()) * 100, 1))

# summarize by task
summaryTask = dataset %>% 
  group_by(subjectID, wave, task) %>% 
  summarise(nVols = sum(trash, na.rm = T),
            percent = round((sum(trash, na.rm = T) / n()) * 100, 1))

# print all trash volumes
summaryTrash = dataset %>%
  filter(trash == 1) %>%
  select(subjectID, wave, task, run, volume, trash)

# create the summary directory if it does not exist
if (!file.exists(outputDir)) {
  message(paste0(outputDir, ' does not exist. Creating it now.'))
  dir.create(outputDir, recursive = TRUE)
}

# write files
write.csv(summaryRun, file.path(outputDir, paste0(study, '_summaryRun.csv')), row.names = FALSE)
write.csv(summaryTask, file.path(outputDir, paste0(study, '_summaryTask.csv')), row.names = FALSE)
write.csv(summaryTrash, file.path(outputDir, paste0(study, '_trashVols.csv')), row.names = FALSE)

#------------------------------------------------------
# write rps
#------------------------------------------------------
# select relevant data
rps = dataset %>%
  select(subjectID, wave, task, run, volume, X, Y, Z, RotX, RotY, RotZ, trash)

if (noEuclidean == FALSE) {
  message('Transforming realignment parameters to Euclidean distance')
  # ouput Euclidean distance and it's derivative rather than the original realignment parameters
  
  # define function to calculate Euclidean distance (i.e. the L2 norm)
  l2norm3ddf = function(a,b,c){
    aDF = data.frame(a,b,c)
    apply(aDF, 1, function(vect) norm(matrix(vect), 'f'))
  }
  
  # For the radian to arc-length conversion, remember: "An angle of 1 radian 
  # refers to a central angle whose subtending arc is equal in length to the 
  # radius." http://www.themathpage.com/aTrig/arc-length.htm
  # If we multiply the radian output of the realignment parameters by the average 
  # head radius of 50mm, we get a rotational displacement from the origin at the 
  # outside of an average skull.
  rps = rps %>%
    group_by(subjectID, wave, task, run) %>%
    mutate(RotX = 50*RotX,
           RotY = 50*RotY,
           RotZ = 50*RotZ,
           euclidean_trans = l2norm3ddf(X, Y, Z),
           euclidean_rot = l2norm3ddf(RotX, RotY, RotZ),
           euclidean_trans_deriv = c(0, diff(euclidean_trans)),
           euclidean_rot_deriv = c(0, diff(euclidean_rot))) %>%
    select(subjectID, wave, task, run, volume, euclidean_trans, euclidean_rot, euclidean_trans_deriv, euclidean_rot_deriv, trash)
  
}

# write files
if (noRP == FALSE) {
  message(sprintf('--------Writing text files to %s--------', outputDir))
  
  # create the subject output directories if they do not exist
  for (sub in unique(rps$subjectID)) {
    subDir = file.path(outputDir, sprintf("sub-%s", sub))
    if (!file.exists(subDir)) {
      message(paste0(subDir, ' does not exist. Creating it now.'))
      dir.create(subDir, recursive = TRUE)
    }
  }
  
  # write the files
  if (ses == TRUE) {
    fnameString = "file.path(.$subDir[[1]], sprintf('sub-%s_ses-%s_task-%s_run-%s_desc-motion_regressors.txt', .$subjectID[[1]], .$wave[[1]], .$task[[1]], .$run[[1]]))" 
  } else {
    fnameString = "file.path(.$subDir[[1]], sprintf('sub-%s_task-%s_run-%s_desc-motion_regressors.txt', .$subjectID[[1]], .$task[[1]], .$run[[1]]))" 
  }
  
  if (noNames == TRUE) {
    rp_files_written = rps %>%
      mutate(subDir = file.path(outputDir, sprintf("sub-%s", subjectID))) %>%
      select(subDir, everything()) %>%
      arrange(subjectID, wave, task, run, volume) %>%
      group_by(subjectID, wave, task, run, subDir) %>%
      do({
        fname = eval(parse(text = fnameString))
        write.table(
          .[,-c(1:6)],
          fname,
          quote = F,
          sep = '\t',
          row.names = F,
          col.names = F)
        data.frame(rp_file_name = fname)
      })
  } else {
    rp_files_written = rps %>%
      mutate(subDir = file.path(outputDir, sprintf("sub-%s", subjectID))) %>%
      select(subDir, everything()) %>%
      arrange(subjectID, wave, task, run, volume) %>%
      group_by(subjectID, wave, task, run, subDir) %>%
      do({
        fname = eval(parse(text = fnameString))
        write.table(
          .[,-c(1:6)],
          fname,
          quote = F,
          sep = '\t',
          row.names = F,
          col.names = T)
        data.frame(rp_file_name = fname)
      })
  }
}

#------------------------------------------------------
# write plots
#------------------------------------------------------
# plot indicators values as a function of time for the motion indicators specified in config.R
if (noPlot == FALSE) {
  message(sprintf('--------Writing plots to %s--------', outputDir))
  
  # create the subject output directories if they do not exist
  for (sub in unique(rps$subjectID)) {
    subDir = file.path(outputDir, sprintf("sub-%s", sub))
    if (!file.exists(subDir)) {
      message(paste0(subDir, ' does not exist. Creating it now.'))
      dir.create(subDir, recursive = TRUE)
    }
  }
  
  # save the plots
  if (ses == TRUE) {
    fnameString = "file.path(.$subDir[[1]], sprintf('sub-%s_ses-%s_task-%s_run-%s%s', .$subjectID[[1]], .$wave[[1]], .$task[[1]], .$run[[1]], figFormat))" 
    pnameString = "sprintf('%s  %s  %s  %s', .$subjectID[[1]], .$wave[[1]], .$task[[1]], .$run[[1]])"
  } else {
    fnameString = "file.path(.$subDir[[1]], sprintf('sub-%s_task-%s_run-%s%s', .$subjectID[[1]], .$task[[1]], .$run[[1]], figFormat))" 
    pnameString = "sprintf('%s  %s  %s', .$subjectID[[1]], .$task[[1]], .$run[[1]])"
  }
  
  
  plots_written = dataset %>% 
    mutate(label = ifelse(grepl(1, trash), as.character(volume), ''),
           code = ifelse(trash == 1, 'trash', NA),
           subDir = file.path(outputDir, sprintf("sub-%s", subjectID))) %>%
    gather(indicator, value, figIndicators) %>%
    group_by(subjectID, wave, task, run) %>%
    do({
      plot = ggplot(., aes(x = volume, y = value)) +
        geom_line(data = filter(., subjectID == .$subjectID[[1]] & wave == .$wave[[1]] & task == .$task[[1]] & run == .$run[[1]]), size = .25) +
        geom_point(data = subset(filter(., subjectID == .$subjectID[[1]] & wave == .$wave[[1]] & task == .$task[[1]] & run == .$run[[1]]), !is.na(code)), aes(color = code), size = 4) +
        geom_text(data = filter(., subjectID == .$subjectID[[1]] & wave == .$wave[[1]] & task == .$task[[1]] & run == .$run[[1]]), aes(label = label), size = 2) +
        facet_grid(indicator ~ ., scales = 'free') +
        scale_color_manual(values = "#E4B80E") +
        labs(title = eval(parse(text = pnameString)),
             y = "value\n",
             x = "\nvolume") +
        theme_minimal(base_size = 10) +
        theme(legend.position = "none")
      ggsave(plot, file = eval(parse(text = fnameString)), height = figHeight, width = figWidth, dpi = figDPI)
      data.frame()
    })
}
