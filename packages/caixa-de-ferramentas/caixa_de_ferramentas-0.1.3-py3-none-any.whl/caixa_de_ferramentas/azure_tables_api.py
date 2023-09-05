from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceExistsError


class TableAPI:

    def __init__(self, storage_account, credential):
        endpoint=f"https://{storage_account}.table.core.windows.net/"
        self.table_service_client =TableServiceClient(endpoint=endpoint, credential=credential)


    def create_table(self, table_name):
        try: table_client = self.table_service_client.create_table(table_name=table_name)
        except ResourceExistsError: 
            print(f'Table {table_name} already exists')
            table_client = self.table_service_client.get_table_client(table_name)
        return table_client


    def delete_table(self, table):
        table_client = self.table_service_client.get_table_client(table)
        table_client.delete_table()
        return table_client


    def query_table(self, table, query):
        table_client = self.table_service_client.get_table_client(table)
        query_result = table_client.query_entities(query)
        return [dict(row) for row in query_result]
    

    def insert_entity(self, table, entity):
        table_client = self.table_service_client.get_table_client(table)
        table_client.create_entity(entity=entity)
        return table_client
    

    def get_entity(self, table, partition_key, row_key):
        table_client = self.table_service_client.get_table_client(table)
        entity = table_client.get_entity(partition_key, row_key)
        return dict(entity)


    def update_entity(self, table, entity, mode='REPLACE'):
        table_client = self.table_service_client.get_table_client(table)
        table_client.update_entity(entity=entity)


if __name__ == '__main__':
    pass