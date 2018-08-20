# auto-motion-fmriprep
## FLUX analyses to be run on the HPC

# load packages and config file
# load/install packages
osuRepo = 'http://ftp.osuosl.org/pub/cran/'

if(!require(tidyverse)){
  install.packages('tidyverse',repos=osuRepo)
}
if(!require(caret)){
  install.packages('caret',repos=osuRepo)
}
if(!require(caTools)){
  install.packages('caTools',repos=osuRepo)
}
if(!require(reshape2)){
  install.packages('reshape2',repos=osuRepo)
}
if(!require(PRROC)){
  install.packages('PRROC',repos=osuRepo)
}
if(!require(purrr)){
  install.packages('purrr',repos=osuRepo)
}
if(!require(pROC)){
  install.packages('pROC',repos=osuRepo)
}
if(!require(doParallel)){
  install.packages('doParallel',repos=osuRepo)
}

# source the config file
source('config_hpc.R')

# load confound files
file_list = list.files(confoundDir, pattern = 'confounds.tsv', recursive = TRUE)

if (!file.exists(paste0(homeDir,"/tag_tds.csv"))) {
  for (file in file_list){
    # if the merged dataset doesn't exist, create it
    if (!exists('dataset')){
      filePattern = paste(subPattern, wavePattern, taskPattern, runPattern, 'bold_confounds.tsv', sep = "_")
      dataset = read_tsv(paste0(confoundDir, file)) %>% 
        mutate(file = file) %>%
        extract(file, c('subjectID', 'wave', 'task', 'run'),
                file.path('.*', 'sub-.*','ses-wave.*', 'func', filePattern)) %>%
        mutate(wave = as.integer(wave),
               run = as.integer(run),
               stdDVARS = as.numeric(ifelse(stdDVARS %in% "n/a", NA, stdDVARS)),
               `non-stdDVARS` = as.numeric(ifelse(`non-stdDVARS` %in% "n/a", NA, `non-stdDVARS`)),
               `vx-wisestdDVARS` = as.numeric(ifelse(`vx-wisestdDVARS` %in% "n/a", NA, `vx-wisestdDVARS`)),
               FramewiseDisplacement = as.numeric(ifelse(FramewiseDisplacement %in% "n/a", NA, FramewiseDisplacement)),
               volume = row_number()) %>%
        select(subjectID, wave, task, run, volume, everything())
    }
    
    # if the merged dataset does exist, append to it
    else {
      filePattern = paste(subPattern, wavePattern, taskPattern, runPattern, 'bold_confounds.tsv', sep = "_")
      tmp = read_tsv(paste0(confoundDir, file)) %>% 
        mutate(file = file) %>%
        extract(file, c('subjectID', 'wave', 'task', 'run'),
                file.path('sub-.*','ses-wave.*', 'func', filePattern)) %>%
        mutate(wave = as.integer(wave),
               run = as.integer(run),
               stdDVARS = as.numeric(ifelse(stdDVARS %in% "n/a", NA, stdDVARS)),
               `non-stdDVARS` = as.numeric(ifelse(`non-stdDVARS` %in% "n/a", NA, `non-stdDVARS`)),
               `vx-wisestdDVARS` = as.numeric(ifelse(`vx-wisestdDVARS` %in% "n/a", NA, `vx-wisestdDVARS`)),
               FramewiseDisplacement = as.numeric(ifelse(FramewiseDisplacement %in% "n/a", NA, FramewiseDisplacement)),
               volume = row_number()) %>%
        select(subjectID, wave, task, run, volume, everything())
      dataset = bind_rows(dataset, tmp)
      rm(tmp)
    }
    write.csv(dataset, paste0(homeDir,"/tag_tds.csv"), row.names = FALSE)
  }
} else {
  dataset = read.csv(paste0(homeDir,"/tag_tds.csv"), stringsAsFactors = FALSE)
}

dataset = dataset %>%
  mutate(sub.run = paste(subjectID, task, run, sep = "_"))

# load hand coded data and merge

coded.tds = read.csv(paste0(homeDir,"/tds_artifacts.csv") %>%
  extract(run, c("task", "run"), "([a-z]+)([0-9]{1})") %>%
  mutate(run = as.integer(run),
         sub.run = paste(subjectID, task, run, sep = "_"),
         subjectID = as.character(subjectID),
         no.artifacts = ifelse(intensity == 0 & striping == 0, 1, NA)) %>%
  select(-fsl.volume)

coded.tag = read.csv(paste0(homeDir,"/tag_artifacts.csv") %>%
  extract(run, c("task", "run"), "([A-Z]+)([0-9]{1})") %>%
  mutate(run = as.integer(run),
         sub.run = paste(subjectID, task, run, sep = "_"),
         volume = fsl.volume + 1) %>%
  select(-fsl.volume) 

coded = bind_rows(coded.tag, coded.tds)

sub_run = unique(coded$sub.run)

joined = left_join(dataset, coded, by = c("subjectID", "task", "run", "volume", "sub.run")) %>%
  mutate(artifact = ifelse(striping == 2, 1, 0),
         artifact = ifelse(is.na(artifact), 0, artifact),
         X.diff = X - lag(X),
         Y.diff = Y - lag(Y),
         Z.diff = Z - lag(Z),
         RotX.diff = RotX - lag(RotX),
         RotY.diff = RotX - lag(RotY),
         RotZ.diff = RotX - lag(RotZ)) %>%
  filter(sub.run %in% sub_run) %>%
  select(subjectID, wave, task, run, volume, artifact, striping, intensity, everything())

# machine learning
## split the data 

set.seed(101) 
ml.data = joined %>%
  select(-c(subjectID, wave, task, run, volume, no.artifacts, sub.run, striping, intensity, starts_with("NonSteady"), starts_with("Cosine"))) %>%
  mutate(artifact = as.factor(ifelse(artifact == 1, "yes", "no")))

# replace NAs with 0
ml.data[is.na(ml.data)] = 0

# subset dataset into development and holdout samples
sample.dev = sample.split(ml.data$artifact, SplitRatio = .8)
dev = subset(ml.data, sample.dev == TRUE)
holdout = subset(ml.data, sample.dev == FALSE)

# subset development sample into training and testing sets
sample = sample.split(dev$artifact, SplitRatio = .75)
training = subset(dev, sample == TRUE)
testing = subset(dev, sample == FALSE)


## run models

Run the best performing models  
* SVM
* RF
* RF with derivatives

### RF with derivatives for realignment parameters

model = paste0(homeDir,"/models/rf_diffs_dev.rds")

if (file.exists(model)) {
  rf_diffs = readRDS(model)
  
} else {
  # turn on parallelization
  cl <- makePSOCKcluster(5)
  registerDoParallel(cl)
  
  # set seed
  set.seed(1995)
  
  # set control function
  ctrl = trainControl(method = "repeatedcv",
                      number = 10,
                      repeats = 5,
                      summaryFunction = twoClassSummary,
                      savePredictions = TRUE,
                      classProbs = TRUE)
  timestamp()
  rf_diffs = train(artifact ~ .,
                   data = dev,
                   method = "rf",
                   metric = "ROC",
                   trControl = ctrl,  
                   preProcess = c("center","scale"))
  timestamp()
  saveRDS(rf_diffs, paste0(homeDir,"/models/rf_diffs_dev.rds"))
  
  # stop parallelization
  stopCluster(cl)
  
}


### exclude derivatives and re-split

set.seed(101) 
ml.data2 = joined %>%
  select(-c(subjectID, wave, task, run, volume, no.artifacts, sub.run, striping, intensity, contains("diff"), starts_with("NonSteady"), starts_with("Cosine"))) %>%
  mutate(artifact = as.factor(ifelse(artifact == 1, "yes", "no")))

# replace NAs with 0
ml.data2[is.na(ml.data2)] = 0

# subset dataset into development and holdout samples
sample.dev2 = sample.split(ml.data2$artifact, SplitRatio = .8)
dev2 = subset(ml.data2, sample.dev == TRUE)
holdout2 = subset(ml.data2, sample.dev == FALSE)

# subset development sample into training and testing sets
sample2 = sample.split(dev2$artifact, SplitRatio = .75)
training2 = subset(dev2, sample == TRUE)
testing2 = subset(dev2, sample == FALSE)


### RF model without derivatives

model = paste0(homeDir,"/models/rf_dev.rds")

if (file.exists(model)) {
  rf_diffs = readRDS(model)
  
} else {
  # turn on parallelization
  cl <- makePSOCKcluster(5)
  registerDoParallel(cl)
  
  # set seed
  set.seed(1995)
  
  # set control function
  ctrl = trainControl(method = "repeatedcv",
                      number = 10,
                      repeats = 5,
                      summaryFunction = twoClassSummary,
                      savePredictions = TRUE,
                      classProbs = TRUE)
  
  # use rf_diff seeds
  ctrl$seeds = rf_diffs$control$seeds
  
  # run model
  timestamp()
  rf = train(artifact ~ .,
             data = dev2,
             method = "rf",
             metric = "ROC",
             trControl = ctrl,  
             preProcess = c("center","scale"))
  timestamp()
  saveRDS(rf, paste0(homeDir,"/models/rf_dev.rds"))
  
  # stop parallelization
  stopCluster(cl)
  
}

### SVM model without derivatives

model = paste0(homeDir,"/models/svm_dev.rds")

if (file.exists(model)) {
  svm = readRDS(model)
  
} else {
  # turn on parallelization
  cl <- makePSOCKcluster(5)
  registerDoParallel(cl)
  
  # set seed
  set.seed(1995)
  
  # set control function
  ctrl = trainControl(method = "repeatedcv",
                      number = 10,
                      repeats = 5,
                      summaryFunction = twoClassSummary,
                      savePredictions = TRUE,
                      classProbs = TRUE)
  # use rf_diff seeds
  ctrl$seeds = rf_diffs$control$seeds
  
  # run model
  timestamp()
  svm = train(artifact ~ .,
              data = dev2,
              method = "svmRadial",
              metric = "ROC",
              trControl = ctrl,  
              preProcess = c("center","scale"))
  timestamp()
  saveRDS(svm, paste0(homeDir,"/models/svm_dev.rds"))
  
  # stop parallelization
  stopCluster(cl)
  
}

### SVM model with derivatives

model = paste0(homeDir,"/models/svm_diffs_dev.rds")

if (file.exists(model)) {
  svm_diffs = readRDS(model)
  
} else {
  # turn on parallelization
  cl <- makePSOCKcluster(5)
  registerDoParallel(cl)
  
  # set seed
  set.seed(1995)
  
  # set control function
  ctrl = trainControl(method = "repeatedcv",
                      number = 10,
                      repeats = 5,
                      summaryFunction = twoClassSummary,
                      savePredictions = TRUE,
                      classProbs = TRUE)
  # use rf_diff seeds
  ctrl$seeds = rf_diffs$control$seeds
  
  # run model
  timestamp()
  svm_diffs = train(artifact ~ .,
                    data = dev,
                    method = "svmRadial",
                    metric = "ROC",
                    trControl = ctrl,  
                    preProcess = c("center","scale"))
  timestamp()
  saveRDS(svm_diffs, paste0(homeDir,"/models/svm_diffs_dev.rds")
          
          # stop parallelization
          stopCluster(cl)
          
}