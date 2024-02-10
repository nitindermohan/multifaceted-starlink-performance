# MNO List

The `mno_list_withasn.csv` has been curated to contain the top mobile network operators of all countries in which Starlink is available. This table has been last updated on October 13th 2023.

## Accessing ASRANK data

To access the asrank data, we use the [AS Rank v2.1 GraphQL API](https://api.asrank.caida.org/dev/docs). First, we manually curate the list of mobile network operators and their respective autonomous system numbers, and then use the API. The code to generate the table is as follows:

```python
import json
import requests

# 1. We manually curate the dataframe containing "CountryName", "MobileOperator", and "ASN" in the variable `mno_df`

# 2. Fetching Caida data for each ASN in the `mno_df` dataframe
URL = "https://api.asrank.caida.org/v2/graphql"
decoder = json.JSONDecoder()
encoder = json.JSONEncoder()

def query_asn(asn):
    query = AsnQuery(asn)
    request = requests.post(URL,json={'query':query})
    if request.status_code == 200:
        return request.json()
    else:
        print ("Query failed to run returned code of %d " % (request.status_code))
        return None

def AsnQuery(asn): 
    return """{
        asn(asn:"%i") {
            asn
            asnName
            rank
            country {
                iso
                name
            }
            asnDegree {
                provider
                peer
                customer
                total
                transit
                sibling
            }
            announcing {
                numberPrefixes
                numberAddresses
            }
        }
    }""" % (int(asn[2:]))

results = []
for _, row in mno_df.iterrows():
    results.append(query_asn(row["ASN"])["data"]["asn"])
caida_df = pd.DataFrame(results)
caida_df = caida_df.set_index("asn")

# 3. Add an asrank column into the `mno_df` dataframe

def getrank(asn):
    return caida_df.loc[[asn[2:]]].iloc[0]["rank"]
mno_df["asrank"] = mno_df["ASN"].apply(getrank)

# 4. Store `mno_df` as a .csv file

mno_df.sort_values(["CountryName", "asrank"])[["CountryName", "MonileOperator", "ASN", "asrank"]].set_index("CountryName").to_csv("mno_list_withasn.csv")
```
