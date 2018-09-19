# This script loads the fmriprep confound files, applies a machine learning classifier to 
# predict motion artifacts, and returns summaries by task, task and run, and trash volumes only. 
# It will also export new rp_txt files if writeRP = TRUE and plots if writePlots = TRUE.

# Inputs:
# * config.R = configuration file with user defined variables and paths

# Outputs:
# * study_summaryRun.csv = CSV file with summary by task and run
# * study_summaryTask.csv = CSV file with summary by task only
# * study_trashVols.csv = CSV file with trash volumes only
# * if writeRP = TRUE, rp_txt files will be written to rpDir
# * if writePlots = TRUE, plots for each subjects will be written to plotDir

#------------------------------------------------------
# load/install packages
#------------------------------------------------------
osuRepo = 'http://ftp.osuosl.org/pub/cran/'

if (!require(tidyverse)) {
  install.packages('tidyverse', repos = osuRepo)
}

#------------------------------------------------------
# source the config file
#------------------------------------------------------
source('config.R')

#------------------------------------------------------
# load confound files
#------------------------------------------------------
fileList = list.files(confoundDir, pattern = paste(subPattern, wavePattern, taskPattern, runPattern, 'bold_confounds.tsv', sep = "_"), recursive = TRUE)

for (file in fileList) {
  
  # if the merged dataset doesn't exist, create it
  if (!exists('dataset')) {
    filePattern = paste(subPattern, wavePattern, taskPattern, runPattern, 'bold_confounds.tsv', sep = "_")
    dataset = read_tsv(file.path(confoundDir, file)) %>% 
      mutate(file = file) %>%
      extract(file, c('subjectID', 'wave', 'task', 'run'),
              file.path('sub-.*','ses-.*', 'func', filePattern)) %>%
      mutate(wave = as.integer(wave),
             run = as.integer(run),
             stdDVARS = as.numeric(ifelse(stdDVARS %in% "n/a", 0, stdDVARS)),
             `non-stdDVARS` = as.numeric(ifelse(`non-stdDVARS` %in% "n/a", 0, `non-stdDVARS`)),
             `vx-wisestdDVARS` = as.numeric(ifelse(`vx-wisestdDVARS` %in% "n/a", 0, `vx-wisestdDVARS`)),
             FramewiseDisplacement = as.numeric(ifelse(FramewiseDisplacement %in% "n/a", 0, FramewiseDisplacement)),
             volume = row_number()) %>%
      select(subjectID, wave, task, run, volume, everything())
    colnames(dataset) = gsub('-', '.', colnames(dataset))
  }
  
  # if the merged dataset does exist, append to it
  else {
    filePattern = paste(subPattern, wavePattern, taskPattern, runPattern, 'bold_confounds.tsv', sep = "_")
    tmp = read_tsv(file.path(confoundDir, file)) %>% 
      mutate(file = file) %>%
      extract(file, c('subjectID', 'wave', 'task', 'run'),
              file.path('sub-.*','ses-.*', 'func', filePattern)) %>%
      mutate(wave = as.integer(wave),
             run = as.integer(run),
             stdDVARS = as.numeric(ifelse(stdDVARS %in% "n/a", 0, stdDVARS)),
             `non-stdDVARS` = as.numeric(ifelse(`non-stdDVARS` %in% "n/a", 0, `non-stdDVARS`)),
             `vx-wisestdDVARS` = as.numeric(ifelse(`vx-wisestdDVARS` %in% "n/a", 0, `vx-wisestdDVARS`)),
             FramewiseDisplacement = as.numeric(ifelse(FramewiseDisplacement %in% "n/a", 0, FramewiseDisplacement)),
             volume = row_number()) %>%
      select(subjectID, wave, task, run, volume, everything())
    colnames(tmp) = gsub('-', '.', colnames(tmp))
    dataset = bind_rows(dataset, tmp)
    rm(tmp)
  }
}

#------------------------------------------------------
# apply classifier
#------------------------------------------------------
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
if (!file.exists(summaryDir)) {
  message(paste0(summaryDir, ' does not exist. Creating it now.'))
  dir.create(summaryDir)
}

# write files
write.csv(summaryRun, file.path(summaryDir, paste0(study, '_summaryRun.csv')), row.names = FALSE)
write.csv(summaryTask, file.path(summaryDir, paste0(study, '_summaryTask.csv')), row.names = FALSE)
write.csv(summaryTrash, file.path(summaryDir, paste0(study, '_trashVols.csv')), row.names = FALSE)

#------------------------------------------------------
# write rps
#------------------------------------------------------
# select relevant data
rps = dataset %>%
  select(subjectID, wave, task, run, volume, X, Y, Z, RotX, RotY, RotZ, trash)

# write files
if (writeRP) {
  if (writeEuclidean) {
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
             trans = l2norm3ddf(X, Y, Z),
             rot = l2norm3ddf(RotX, RotY, RotZ),
             deriv.trans = c(0, diff(trans)),
             deriv.rot = c(0, diff(rot))) %>%
      select(subjectID, wave, task, run, volume, trans, rot, deriv.trans, deriv.rot, trash)
    
  }
  
  # create the rp directory if it does not exist
  if (!file.exists(rpDir)) {
    message(paste0(rpDir, ' does not exist. Creating it now.'))
    dir.create(rpDir)
  }
  
  # write the files
  rp_files_written = rps %>%
    arrange(subjectID, wave, task, run, volume) %>%
    group_by(subjectID, wave, task, run) %>%
    do({
      fname = file.path(rpDir, paste('rp_', .$subjectID[[1]], '_', .$wave[[1]], '_', .$task[[1]], '_', .$run[[1]], '.txt', sep = ''))
      write.table(
        .[,-c(1:5)],
        fname,
        quote = F,
        sep = '   ',
        row.names = F,
        col.names = F)
      data.frame(rp_file_name = fname)
    })
}

#------------------------------------------------------
# write plots
#------------------------------------------------------
# plot indicators values as a function of time for the motion indicators specified in config.R
if (writePlot) {
  
  # create the plot directory if it does not exist
  if (!file.exists(plotDir)) {
    message(paste0(plotDir, ' does not exist. Creating it now.'))
    dir.create(plotDir)
  }
  
  # save the plots
  plots_written = dataset %>% 
    mutate(label = ifelse(grepl(1, trash), as.character(volume), ''),
           code = ifelse(trash == 1, 'trash', NA)) %>%
    gather(indicator, value, figIndicators) %>%
    group_by(subjectID, wave, task, run) %>%
    do({
      plot = ggplot(., aes(x = volume, y = value)) +
        geom_line(data = filter(., subjectID == .$subjectID[[1]] & wave == .$wave[[1]] & task == .$task[[1]] & run == .$run[[1]]), size = .25) +
        geom_point(data = subset(filter(., subjectID == .$subjectID[[1]] & wave == .$wave[[1]] & task == .$task[[1]] & run == .$run[[1]]), !is.na(code)), aes(color = code), size = 4) +
        geom_text(data = filter(., subjectID == .$subjectID[[1]] & wave == .$wave[[1]] & task == .$task[[1]] & run == .$run[[1]]), aes(label = label), size = 2) +
        facet_grid(indicator ~ ., scales = 'free') +
        scale_color_manual(values = "#E4B80E") +
        labs(title = paste0(.$subjectID[[1]], "  ", .$wave[[1]], "  ", .$task[[1]], "  ", .$run[[1]]),
          y = "value\n",
          x = "\nvolume") +
        theme_minimal(base_size = 10) +
        theme(legend.position = "none")
      ggsave(plot, file = file.path(plotDir, paste0(.$subjectID[[1]], '_', .$wave[[1]], '_', .$task[[1]], '_', .$run[[1]], figFormat)), height = figHeight, width = figWidth, dpi = figDPI)
      data.frame()
    })
}
