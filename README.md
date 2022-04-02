<!-- # Dunebuggy

![Alt text](./dune-buggy.svg) -->

<h1 align="center">
  <br>
  <img src="./assets/dune-buggy.svg" alt="Dunebuggy" width="300" height="225">
  <br>
  <div style="sans-serif"><b>Dunebuggy</b></p>
</h1>

<div align="center">
A lightweight (unofficial) Python SDK for <a href=https://dune.xyz/home> Dune.xyz</a>
<br>

[Installation](#installation) •
[Getting started](#getting-started) •
[Roadmap](#roadmap) •
[Notes](#notes)

</div>

## Installation

```sh
pip install dunebuggy
```

## Getting started

### Retrieving a public query

To retrieve a query, all we'll need is the `query_id` for the public query we're interested in. In the below example we can take a look at the popular ["Custom NFT Floor Tracker" query by @smaroo](https://dune.xyz/queries/83579) (The `query_id` below can be found in the URL).

```python
from dunebuggy import Dune

dune = Dune()
query = dune.fetch_query(83579)
```

`query` here is a `DuneQuery` object, we can get the `pandas` DataFrame for the query output bf calling `df` on the object

```python
print(query.df.head())
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Floor (Approx)</th>
      <th>Time Interval</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.122649</td>
      <td>2021-06-01T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.130000</td>
      <td>2021-06-02T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.193455</td>
      <td>2021-06-03T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.189000</td>
      <td>2021-06-04T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.189930</td>
      <td>2021-06-05T00:00:00+00:00</td>
    </tr>
  </tbody>
</table>
</div>

We can also take a look at some basic information about the returned query with `query.info`

```python
print(query.info)
```

    {'name': 'Custom NFT Floor Tracker',
     'author': '@smaroo',
     'length': 264,
     'query_id': 83579,
     'result_id': UUID('e5aef8a0-1453-44d1-a27b-f576ea2b3ba2'),
     'job_id': UUID('ec680fa9-217f-44c5-b223-56730cd07473'),
     'columns': ['Time Interval', 'Floor (Approx)']}

Some queries in Dune are "parameterized", meaning that the author exposes certain variables for the user to enter custom values. The example query (83579) happens to be parameterized, we can verify this by inspecting `query.parameters`

```python
print(query.parameters)
```

    [QueryParameter(key='Enter NFT Contract Address', type='text', value='xc3f733ca98e0dad0386979eb96fb1722a1a05e69', enumOptions=None),
     QueryParameter(key='Floor Time Interval', type='enum', value='Day', enumOptions=['Day', 'Hour']),
     QueryParameter(key='Start Date', type='datetime', value='2021-06-01 00:00:00', enumOptions=None)]

If you'd like to run this query with your own custom parameters, all we'll need to do is take the parameters from from the initial query, change the values to what we want, and re-fetch the query.

Below we are replacing the old NFT contract address param with a new one ([the contract address for BAYC](https://etherscan.io/address/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d))

```python
params = query.parameters

# Replacing with contract address for BAYC
params[0].value = 'xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'
custom_query = dune.fetch_query(83579, parameters=params)
```

Note: You can also create a fresh set of parameters by importing `QueryParameter` from `dunebuggy.models.query` and adding the values to the new object.

```python
from dunebuggy.models.query import QueryParameter

param_to_change = QueryParameter(
  key='Enter NFT Contract Address',
  value='xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
)
params[0] = param_to_change
custom_query = dune.fetch_query(83579, parameters=params)
```

```python
print(custom_query.info)
```

    {'name': 'Custom NFT Floor Tracker',
     'author': '@smaroo',
     'length': 265,
     'query_id': 83579,
     'result_id': UUID('42a3c13d-5fbd-42bd-86c0-acc9adcdc803'),
     'job_id': UUID('9051ebe7-862f-46d0-9999-b4645659ca56'),
     'columns': ['Time Interval', 'Floor (Approx)']}

Note that the `result_id` and `job_id` here are different, this is because we ran the query with our changed params

```python
print(custom_query.parameters)
```

    [QueryParameter(key='Enter NFT Contract Address', type='text', value='xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D', enumOptions=None),
    QueryParameter(key='Floor Time Interval', type='enum', value='Day', enumOptions=['Day', 'Hour']),
    QueryParameter(key='Start Date', type='datetime', value='2021-06-01 00:00:00', enumOptions=None)]

```python
print(custom_query.df.head())
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Floor (Approx)</th>
      <th>Time Interval</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.8000</td>
      <td>2021-06-01T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.8518</td>
      <td>2021-06-02T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.8260</td>
      <td>2021-06-03T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.7400</td>
      <td>2021-06-04T00:00:00+00:00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.8499</td>
      <td>2021-06-05T00:00:00+00:00</td>
    </tr>
  </tbody>
</table>
</div>

### Creating a new query

`dunebuggy` also allows you to create a new using an existing Dune.xyz account.To login just need to pass in your username/password into the `Dune` object.

You can verify your login by inspecting your Dune `user_id`

```python
import os

username = os.environ.get('DUNE_USERNAME')
password = os.environ.get('DUNE_PASSWORD')

dune = Dune(username=username, password=password)
# print(dune.user_id)
```

To create a query now, all we need to do is pass in a `name`, `query_string` and `dataset_id`

We can construct the SQL query by using a raw sql string

```python
query_string = "select * from ethereum.transactions\nLIMIT 100\n"
```

Or we could use a fancy ORM-style library like [pypika](https://github.com/kayak/pypika)

```python
from pypika import Database, Query

ethereum = Database('ethereum')
q = Query.from_(ethereum.transactions).select('*').limit(100)
query_string = q.get_sql(quote_char=None)
print(query_string)
```

    'SELECT * FROM ethereum.transactions LIMIT 100'

Dune requires us to specify a `dataset_id` for each of their supported blockchain datasets upon query creation. The currently supported datasets are the following:

| Blockchain Dataset | Id  |
| ------------------ | --- |
| ETHEREUM           | 4   |
| XDAI               | 6   |
| POLYGON            | 7   |
| OPTIMISM_1         | 8   |
| OPTIMISM_2         | 10  |
| BINANCE            | 9   |
| SOLANA             | 1   |

We can access these integer codes via the `DatasetId` enum

```python
from dunebuggy.models.constants import DatasetId
created_query = dune.create_query("My Query's Name", query_string, DatasetId.ETHEREUM)
```

Our created query can be accessed like any other, you can also log into your Dune account as see it there as well!

```python
print(created_query.df.head())
```

<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>access_list</th>
      <th>block_hash</th>
      <th>block_number</th>
      <th>block_time</th>
      <th>data</th>
      <th>from</th>
      <th>gas_limit</th>
      <th>gas_price</th>
      <th>gas_used</th>
      <th>hash</th>
      <th>index</th>
      <th>max_fee_per_gas</th>
      <th>max_priority_fee_per_gas</th>
      <th>nonce</th>
      <th>priority_fee_per_gas</th>
      <th>success</th>
      <th>to</th>
      <th>type</th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>None</td>
      <td>\x887c665b0c52ccace092d817e984e2e828ef59079295...</td>
      <td>47287</td>
      <td>2015-08-07T08:50:01+00:00</td>
      <td>None</td>
      <td>\xdb312d1d6a2ccc64dd94a3892928bac82b4e8c15</td>
      <td>21000</td>
      <td>100000000000</td>
      <td>21000</td>
      <td>\xd3e6a2fc34066d20bb83020b1ee95b9dc7919fd242bd...</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>\x34bb6978c5a1ad68777ad388c6787df53903430c</td>
      <td>None</td>
      <td>1000000000000000000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>None</td>
      <td>\x4869e218b0a8f5784f16193ac66cbf35c4510ace0c9b...</td>
      <td>48698</td>
      <td>2015-08-07T15:29:53+00:00</td>
      <td>None</td>
      <td>\x48040276e9c17ddbe5c8d2976245dcd0235efa43</td>
      <td>90000</td>
      <td>57550496008</td>
      <td>21000</td>
      <td>\x8ba39f908731171fe96ee4e700e71d170ef8e651fac7...</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>\xd8d0549637b65d58e7fb6cbdd11530b399d1ddac</td>
      <td>None</td>
      <td>100000000000000000000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>None</td>
      <td>\xab9491b62b16bd928b281a83db82483584c22aeebc0d...</td>
      <td>49051</td>
      <td>2015-08-07T17:03:48+00:00</td>
      <td>None</td>
      <td>\x8686578c4f7c75246f548299d6ffdac3b67b5cd1</td>
      <td>90000</td>
      <td>57178423039</td>
      <td>21000</td>
      <td>\x57f8ba638903d6335e211eb470159587c73316788880...</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>\x87abffa6b80f712c852a9558120ba6611f0b5e46</td>
      <td>None</td>
      <td>45150000000000000000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>None</td>
      <td>\x1f9adc2190701ca3085b28252e4f1f467d980f763dad...</td>
      <td>49174</td>
      <td>2015-08-07T17:41:03+00:00</td>
      <td>None</td>
      <td>\x18e4ce47483b53040adbab35172c01ef64506e0c</td>
      <td>90000</td>
      <td>58589751415</td>
      <td>21000</td>
      <td>\xb8280da44f8d35011c3f431f7d1a82213477a4e742de...</td>
      <td>2</td>
      <td>None</td>
      <td>None</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>\xfb26ae2d3621829472555fbd11bb2a324b7a5c57</td>
      <td>None</td>
      <td>10000000000000000000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>None</td>
      <td>\xf1f392fd197a149afe9f8843d7ba759d1a9f79d1ef62...</td>
      <td>49938</td>
      <td>2015-08-07T21:06:21+00:00</td>
      <td>None</td>
      <td>\xc6bf5b6558f2ee21f2e43d9ff9b5408a0cb89413</td>
      <td>90000</td>
      <td>71214529679</td>
      <td>21000</td>
      <td>\x538e1664c12c55287c98dc5dd248f60c642cbbbd7a18...</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>4</td>
      <td>None</td>
      <td>None</td>
      <td>\x33a3f479f6c3e7f91128348490d1f7e8d2a0fab5</td>
      <td>None</td>
      <td>5000000000000000000</td>
    </tr>
  </tbody>
</table>
</div>

### Saving to CSV

To save a query to a CSV, we can take advantage of the `to_csv` method on our `df`

```python
created_query.df.to_csv('my_test_data.csv')
```

## Roadmap

- [ ] Cleanup punding TODO comments
- [ ] Add support for embedding Dune graphs/ plotting w/ Dune style colors
- [ ] Add tests (lol)
- [ ] Add support for query updating
- [ ] Investigate whether dashboard support makes sense?
- [ ] Investigate whether there is a max row limit for data returned, if so, query in batches?
- [ ] Better formatting for certain returned columns (links etc..)
- [ ] Add Documentation (Sphinx or something else)

## Notes

_This project was inspired by the [itzemstar's duneanalytics repo](https://github.com/itzmestar/duneanalytics)_

_README image is from the [IAN Symbols dataset](https://ian.umces.edu/media-library/symbols/)_
