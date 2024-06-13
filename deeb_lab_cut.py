import deeplabcut


project_name = 'firstVersion'
experimenter = 'Flo'
list_of_videos = ['C:/LabData/firstVideo.mp4', 'C:/LabData/secondVideo.mp4', 'C:/LabData/thirdVideo.mp4']
working_directory = 'C:/LabProjects'
config_file_path = 'C:\LabProjects\secondVersion-Flo-2024-06-13/config.yaml'
# deeplabcut.create_new_project(project=project_name,experimenter=experimenter,videos=list_of_videos,working_directory=working_directory)
# deeplabcut.extract_frames(config=config_file_path,mode='automatic',algo='kmeans',userfeedback=False)
deeplabcut.label_frames(config_file_path)
# deeplabcut.create_training_dataset(config_file_path, augmenter_type='imgaug')
# deeplabcut.create_labeled_video('C:/Users/flori/Desktop/First-Try-Flo-2024-05-09/config.yaml','C:/Users/flori/Downloads/m3v1mp4.mp4', fastmode=False, save_frames= True)
deeplabcut.train_network(config=config_file_path, shuffle=[1])
deeplabcut.evaluate_network(config=config_file_path, Shuffles=[1], plotting=True)