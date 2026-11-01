class ClientCollection:
    def __init__(self, clients):
        self.clients = clients

    def get_client_by_id(self, client_id):
        for client in self.clients:
            if client.client_id == client_id:
                return client

        return None

    def clients_by_country(self, country):
        clients_found = []

        for client in self.clients:
            if client.country == country:
                clients_found.append(client)

        return clients_found