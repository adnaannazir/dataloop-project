import dtlpy as dl
import random
from datetime import datetime

def create_dataset(project_name, dataset_name):
    """
    Create a dataset in the specified project.

    Args:
        project_name (str): Name of the project
        dataset_name (str): Name of the dataset

    Returns:
        dl.Dataset: The created dataset object
    """

    try:
        project = dl.projects.get(project_name=project_name)

    except:
        raise Exception(f"Project '{project_name}' not found")

    try:
        dataset = project.datasets.get(dataset_name=dataset_name)
    
    except:
        dataset = project.datasets.create(dataset_name=dataset_name)

    return dataset


def add_utm_info(dataset, items):
    """
    Add utm data to the specified items.

    Args:
        dataset (dl.Dataset): The dataset object that contains the items
        items (list): A list of items to add metadata to
    """

    metadata = {"user": {"UTM": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}}

    filters = dl.Filters()
    filters.add('item_id', 'in', [item.id for item in items])
    dataset.items.update(filters=filters, update_values = metadata)


def add_class_label(label, items):
    """
    Add a classification annotation with the given label to each item in a list of items.

    Parameters:
        label (str): The label for the classification annotation.
        items (list of dl.Item): The list of items to add the classification to.
    """

    for item in items:
        builder = item.annotations.builder()
        builder.add(annotation_definition=dl.Classification(label=label))
        item.annotations.upload(builder)


def upload_annotations(item,builder):
    """
    We use the upload method to upload multiple annotations to Dataloop in a single API call. 
    This way, we can upload multiple annotations in a more efficient way than uploading them one by one.
    """
    # Upload the annotations to Dataloop
    item.annotations.upload(builder)


def add_random_keypoints_with_label(items,label,n):
    """
    Add a point annotation with the label "key" to a random point on one of the items in a dataset.

    Parameters:
        items (list of dl.Item): The list of items in the dataset to add the point annotation to.
        label: The label to be added
        n: The number of random points
    """
    item = random.choice(items)
    builder = item.annotations.builder()

    for _ in range(n):
        x = random.randint(0, item.metadata['system']['width'])
        y = random.randint(0, item.metadata['system']['height'])
        builder.add(annotation_definition=dl.Point(x=x, y=y, label=label))
    
    upload_annotations(item,builder)
    


def select_images_by_label(dataset, label):
    """
    Select only image items that have been labeled as "label" and print their details

    Parameters:
        dataset (dl.Dataset): The dataset object that contains the items
        label: The label on which the filtering happens
    """
    filters = dl.Filters()
    filters.add_join(field='label', values=label, operator=dl.FILTERS_OPERATIONS_EQUAL)
    pages = dataset.items.list(filters=filters)
    for page in pages:
        for item in page:
            ##print(type(item))
            item.print()
          

def get_all_point_annotations(dataset):
    """
    Retrieves all point annotations from the dataset and prints the relevant details as asked in the assignment

    Parameters:
        dataset (dl.Dataset): The dataset object that contains the items
    """
    
    filters = dl.Filters()
    filters.add_join(field='type', values='point')
    pages = dataset.items.list(filters=filters)

    for page in pages:
        for item in page: 
            item.print()
            print(item.annotations.list())


def main():
    ## The login credentials were generated following the documentation.

    if dl.token_expired():
        dl.login_m2m(email="bot.07f0391c-434d-4695-a469-b35cca5764c4@bot.dataloop.ai", password="%7341QoE1DS1*X2j$")

    ## Create dataset
    dataset = create_dataset('DataloopInterview', 'dataset-created-from-script')

    ## Add Labels
    dataset.add_labels([
        dl.Label(tag='class1', color=(255, 100, 0)),
        dl.Label(tag='class2', color=(34, 56, 7)),
        dl.Label(tag='key', color=(100, 14, 150)),
    ])

    ## Upload images from the directory
    dataset.items.upload(local_path='/Users/Shared/dataloop-dataset')
    items = dataset.items.list()[0]


    add_utm_info(dataset, items)
    add_class_label('class1', items[:2])
    add_class_label('class2', items[2:])
    add_random_keypoints_with_label(items,"key",5)
    select_images_by_label(dataset, 'class1')
    get_all_point_annotations(dataset)
    dl.logout()


if __name__ == "__main__":
    main()
