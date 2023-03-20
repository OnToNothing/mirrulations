class PathGenerator:
    """
    A Class which classifies any type of file into the correct directory following our 
    data structure where every path is based on an agencyId, id, docketId and type
    Paths are generated by extracting information from a dockets, documents or comments .json file
    Important Keys:
    ----------
    agencyId: The Governmental Agency Abbreviation from Regulations.gov
    
    id: Everything related to a docket is identified by its id
        Ex of a Docket's 'id': USTR-2015-0010
        Ex of a Document's 'id':  USTR-2015-0010-0001
        Ex of a Comment's 'id': USTR-2015-0010-0002
    type: The value for a json's 'type' key
        Can be a docket, document, comment or attachment
    ...
    Methods
    -------
    get_path(json = dict)
        Looks for the 'type' key in the json and calls the appropriate path generator method for
        the given 'type'
    parse_docket_id(item_id = str)
        If the json does not have the docketId field we must parse out the docketId using 
        split methods.
    get_attributes(json_data, is_docket_json=False)
        Returns the agencyid, docket_id, and item_id from a loaded json object.
        Also handles if a key is not found in the json
    get_docket_json_path(json = dict): 
        Gets the path for a json with the 'dockets' type
    get_document_json_path(json = dict): 
        Gets the path for a json with the 'documents' type
    get_comment_json_path(json = dict): 
        Gets the path for a json with the 'comments' type
    """

    def get_path(self, json):
        if 'data' not in json or json['data'] ==[]:
            return "/unknown/unknown.json"
        if json['data']["type"] == "comments":
            return self.get_comment_json_path(json)
        if json['data']["type"] == "dockets":
            return self.get_docket_json_path(json)
        if json['data']["type"] == "documents":
            return self.get_document_json_path(json)

   
    def _get_nested_keys_in_json(self, json_data, nested_keys, default_value):
        '''
        Gets a value from traversing a series of nested keys in a JSON object.
        default_value is the value that should be returned if any of the nested
        keys are missing from the JSON.
        '''
        json_subset = json_data

        for key in nested_keys:
            if key not in json_subset:
                return default_value
            else:
                json_subset = json_subset[key]

        return json_subset

    def parse_docket_id(self, item_id):
        if item_id is None:
            return "unknown"

        segments = item_id.split('-') # list of segments separated by '-'
        segments_excluding_end = segments[:-1] # drops the last segment
        parsed_docket_id = '-'.join(segments_excluding_end)
        print(f'No DocketId Key found, parsing the "id" key')
        print(f'Id = {item_id}, Parsed DocketId = {parsed_docket_id}')
        return parsed_docket_id


    def get_attributes(self, json_data, is_docket_json=False):
        '''
        Returns the agency, docket id, and item id from a loaded json object.
        '''
        item_id = self._get_nested_keys_in_json(
            json_data, ['data', 'id'], None)
        agency_id = self._get_nested_keys_in_json(
            json_data, ['data', 'attributes', 'agencyId'], None)

        if is_docket_json:
            docket_id = item_id
            item_id = None
        else:
            docket_id = self._get_nested_keys_in_json(
                json_data, ['data', 'attributes', 'docketId'], None)

            if docket_id is None:
                docket_id = self.parse_docket_id(item_id)
                print(f'{item_id} was parsed to get docket id: {docket_id}.')

        # convert None value to respective folder names
        if not is_docket_json and item_id is None:
            item_id = 'unknown'
        if docket_id is None:
            docket_id = 'unknown'
        if agency_id is None:
            agency_id = 'unknown'

        return agency_id, docket_id, item_id

    def get_docket_json_path(self, json): 
        agencyId, docket_id, _ = self.get_attributes(json, is_docket_json=True)

        return f'/{agencyId}/{docket_id}/text-{docket_id}/docket/{docket_id}.json'


    def get_document_json_path(self, json):
        agencyId, docket_id, item_id = self.get_attributes(json)

        return f'/{agencyId}/{docket_id}/text-{docket_id}/documents/{item_id}.json'

    def get_comment_json_path(self, json):
        agencyId, docket_id, item_id = self.get_attributes(json)

        return f'/{agencyId}/{docket_id}/text-{docket_id}/comments/{item_id}.json'
    
    def get_attachment_json_paths(self, json):
        '''
        Given a json, this function will return all attachment paths for 
        n number attachment links
        '''
        agencyId, docket_id, item_id = self.get_attributes(json)

        # contains list of paths for attachments
        attachments = []

        for attachment in json["included"]:
            id = attachment.get("id")
            attributes = attachment["attributes"]
            if (attributes["fileFormats"] and attributes["fileFormats"] != "null" and attributes["fileFormats"] is not None):
                for file_format in attributes["fileFormats"]:
                    if ("fileUrl" in file_format):
                        attachment_name = file_format["fileUrl"].split("/")[-1]
                        attachment_id = item_id + "_" + attachment_name
                        attachments.append(f'/{agencyId}/{docket_id}/binary-{docket_id}/comments_attachments/{attachment_id}')
                    else:
                        print(f"fileUrl did not exist for attachment ID: {id}")
            else:
                print(f"fileFormats did not exist for attachment ID: {id}")

        return attachments
    
    @staticmethod
    def make_attachment_save_path(path):
        '''
        This method takes a complete path to a pdf and makes
        the save path based on paramters in that path.
        Parameters
        ----------
        path : str
            the complete file path for the attachment that is being extracted
            ex. /path/to/pdf/attachment_1.pdf
        '''
        if "comments" in path:
            return path.replace('binary', 'text') \
            .replace('comments_attachments', 'comments_extracted_text/pdfminer') \
            .replace('.pdf', '_extracted.txt') \
        
        return path.replace('binary', 'text') \
            .replace('documents_attachments', 'documents_extracted_text/pdfminer') \
            .replace('.pdf', '_extracted.txt') \
            
