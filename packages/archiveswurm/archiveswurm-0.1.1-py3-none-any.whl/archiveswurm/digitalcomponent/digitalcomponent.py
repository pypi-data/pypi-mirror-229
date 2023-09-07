import json
import requests
from ..archivesspace import ArchivesSpace


class DigitalObjectComponent(ArchivesSpace):
    """Class for working with Digital Object Components in ArchivesSpace."""
    def __init__(self, url="http://localhost:9089", user="admin", password="admin"):
        super().__init__(url, user, password)

    def get_list_of_ids(self, repo_id):
        """Get a list of ids for Digital Object Components in a Repository.

        Args:
            repo_id (int): The id of the repository you are querying.

        Returns:
            list: A list of ints that represent each Digital Object Component in the repository.

        Examples:
            >>> DigitalObjectComponent().get_list_of_ids(2)
            []

        """
        r = requests.get(
            url=f"{self.base_url}/repositories/{repo_id}/digital_object_components?all_ids=true",
            headers=self.headers,
        )
        return r.json()

    def get_by_page(self, repo_id, page=1, page_size=10):
        """Get Digital Object Components on a page.

        Args:
            repo_id (int): The id of the repository you are querying.
            page (int): The page of digital object components you want to get.
            page_size (int): The size of the page you want returned.

        Returns:
            dict: A dict with information about the results plus all matching Digital Object Components.

        Examples:
            >>> DigitalObjectComponent().get_by_page(2, 2, 10)
            {'first_page': 1, 'last_page': 1, 'this_page': 1, 'total': 0, 'results': []}

        """
        r = requests.get(
            url=f"{self.base_url}/repositories/{repo_id}/digital_object_components?page={page}&page_size={page_size}",
            headers=self.headers,
        )
        return r.json()

    def get(self, repo_id, digital_object_component_id):
        """Get a Digital Object Component by id.

        Args:
            repo_id (int): The id of the repository you are querying.
            digital_object_component_id (int): The id of the digital object component you want.

        Returns:
            dict: The digital object component as a dict.

        Examples:
            >>> DigitalObjectComponent().get(2, 2)
            {'lock_version': 0, 'jsonmodel_type': 'digital_object_component', 'suppressed': False, 'display_string': 'test', 'uri': '/repositories/2/digital_object_components/2', 'created_by': 'admin', 'last_modified_by': 'admin', 'create_time': '2021-04-08T14:34:37Z', 'system_mtime': '2021-04-08T14:34:37Z', 'user_mtime': '2021-04-08T14:34:37Z', 'digital_object': {'ref': '/repositories/2/digital_objects/2', 'display_string': 'test'}, 'file_versions': []}

        """
        r = requests.get(
            url=f"{self.base_url}/repositories/{repo_id}/digital_object_components/{digital_object_component_id}",
            headers=self.headers,
        )
        return r.json()
