# GraphQL-DynamoDB

## Inspiration

- [Reading about the internal architecture of Dgraph](https://github.com/dgraph-io/dgraph/blob/main/paper/dgraph.pdf)
  - key-value store underneath the graph api
    - predicate-subject as key
    - objectValue as value
    - sharded by predicate (field name)
- I wondered how far I could get (performance-wise, etc) from just using a single DynamoDB table as the underlying key-value store for a GraphQL API
  - the Partition Key would be the predicate (field name)
  - the Sort Key would be the Node ID (UUID)
  - a single "RefVal" attribute would be the equivalent of Dgraph's objectValue

## Development

- Python's [FastAPI](https://fastapi.tiangolo.com/) with [Strawberry](https://strawberry.rocks/) for the GraphQL layer
- deployed as an AWS Lambda Function
- each field directly resolves using a "get" request for a single item in the DynamoDB table
  - no complex queries or joins necessary under the hood
- relationships are stored as a list of UUIDs and resolved through normal Strawberry field resolution

## Results

- better than expected, considering this implementation is nowhere near what I'd deploy in production
  - I mostly wanted to see how far a completely naive implementation could get me, since it makes adding new node types and fields to the GraphQL API insanely simple (i.e. almost zero schema maintenance overhead)
- queries involving two or three fields across tens of thousands of nodes would return within 1 minute from a cold start

## Next Steps

- aggregate all "gets" for a given field name ("predicate") into a single query
  - currently it sends a separate get request for each field on each node
- use a DataLoader or something similar to cache results in a given request
- implement pagination for results
- (eventually) implement a workaround for the DynamoDB item size limit
  - currently hit with large (25,000+) lists of node references
- (possibly) use DAX to decrease latency of data fetches
