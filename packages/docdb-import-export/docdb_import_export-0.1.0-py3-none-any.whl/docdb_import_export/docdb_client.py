import os
import sys
import pymongo

class DocDbClient:

  # Class variable to hold the document db instance.
  connections = {}

  def __init__(self):
    # Initialize instance variables.
    self.hostname = os.environ.get("DOCDB_HOST")
    self.port = os.environ.get("DOCDB_PORT")
    self.ca_file = os.environ.get("DOCDB_CA_FILE_PATH")
    self.replica_set = os.environ.get("DOCDB_REPLICA_SET")
    self.read_preference = os.environ.get("DOCDB_READ_PREFERENCE")
    self.retry_writes = os.environ.get("DOCDB_RETRY_WRITES")
    self.tls_allow_invalid_hostnames = os.environ.get("DOCDB_TLS_ALLOW_INVALID_HOSTNAMES")
    self.direct_connection=os.environ.get("DOCDB_DIRECT_CONNECTION")

  # This method gets document db connection string, if ssl_true parameter is
  # true, it will return the ssl connection string, otherwise it will return
  # the non-ssl connection string.
  #
  # It will create the ssl connection string in the following format:
  # mongodb://<sample-user>:<password>@sample-cluster.node.us-east-1.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false
  #
  # It will create the non-ssl connection string in the following format:
  # mongodb://<sample-user>:<password>@sample-cluster.node.us-east-1.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
  #
  # It will read all other parameters from instance variables.
  def __get_docdb_connection_string(self, ssl_true = True):
    username = os.environ.get("DOCDB_USERNAME")
    password = os.environ.get("DOCDB_PASSWORD")
    if ssl_true:
      return "mongodb://%s:%s@%s:%s/?tls=true&tlsCAFile=%s&replicaSet=%s&readPreference=%s&retryWrites=%s&tlsAllowInvalidHostnames=%s&directConnection=%s" % (username, password, self.hostname, self.port, self.ca_file, self.replica_set, self.read_preference, self.retry_writes, self.tls_allow_invalid_hostnames, self.direct_connection)
    else:
      return "mongodb://%s:%s@%s:%s/?replicaSet=%s&readPreference=%s&retryWrites=%s&directConnection" % (username, password, self.hostname, self.port, self.replica_set, self.read_preference, self.retry_writes, self.direct_connection)

  # This method gets the document db instance with the given connection name. If
  # the connection is already cached, it will return the cached connection. If
  # the connection is not cached, it will create a new connection and cache it.
  # This method will use the pymongo to connect to the document db.
  def get_instance(self, connection_name, ssl_true = True):
    try:
      if connection_name in DocDbClient.connections:
        return DocDbClient.connections[connection_name]
      else:
        # Get document db connection string.
        docdb_connection_string = self.__get_docdb_connection_string(ssl_true)
        docdb = pymongo.MongoClient(docdb_connection_string)
        DocDbClient.connections[connection_name] = docdb
        return DocDbClient.connections[connection_name]
    except Exception as e:
      print("ERROR: Failed to connect to MongoDB cluster: " + str(e))
      sys.exit(1)

  def disconnect(self, connection_name):
    try:
      if connection_name in DocDbClient.connections:
        DocDbClient.connections[connection_name].close()
        del DocDbClient.connections[connection_name]
    except Exception as e:
      print("ERROR: Failed to disconnect from MongoDB cluster: " + str(e))
      sys.exit(1)
