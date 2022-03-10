

class MockDocumentCount:

    def __init__(self, count_to_return):
        self.count = count_to_return

    def count_documents(self, dummy):
        assert dummy == {}
        return self.count

def create_mock_mongodb(docket_count, document_count, comment_count):
    # needs:
    # * ['mirrulations']
    # * ['mirrulations']['dockets'] (also documents and comments)
    # * .count_documents(param) that returns an int as a string

    collections = {}
    collections['dockets'] = MockDocumentCount(docket_count)
    collections['documents'] = MockDocumentCount(document_count)
    collections['comments'] = MockDocumentCount(comment_count)

    ret = {}
    ret['mirrulations'] = collections

    return ret