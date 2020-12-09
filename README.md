# verify-elements-commitments

Verify revealed assets and/or satoshi for Elements Confidential Transactions.

Alice might need to prove to Bob that an Elements Confidential Transaction sent a certain amount of a certain asset.
Bob using the provided script can _verify_ that the revealed values are correct by checking those against the Confidential Transaction obtained from a trusted source, such as his Elements Core node, or a block explorer.

## Setup

Create and activate a virtualenv (optional):

    virtualenv -p python3 venv
    source venv/bin/activate

Install libwally-core from the
[relased](https://github.com/ElementsProject/libwally-core/releases) wheels, e.g.:

    pip install https://github.com/ElementsProject/libwally-core/releases/download/release_0.8.0/wallycore-0.8.0-cp36-cp36m-linux_x86_64.whl

Or install from source, following
[these instructions](https://github.com/ElementsProject/libwally-core#python).

## Usage

Blinders json may be of 2 kinds: no version or version 0.
Green apps outputs version 0 json, while no version json strings support things such as only revealing the asset or amount.

### Version 0

An incoming transaction:
```
$ python verify-elements-commitments.py --tx data/version0/266ee76b.txt --blinded data/version0/blinders1.json
{
  "txid": "266ee76b6fba86bdd31bdb42e2fbb2d56990fd84af0f325400e50f7621c2ea8b",
  "inputs": [],
  "outputs": [
    {
      "vout": 0,
      "asset": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",
      "satoshi": 100
    }
  ]
}
```

An outgoing transaction:
```
$ python verify-elements-commitments.py --tx data/version0/8a5d8422.txt --blinded data/version0/blinders2.json --input-txs data/version0/5eeaccb0.txt data/version0/3c393ea4.txt data/version0/79cb0bdc.txt data/version0/5c1ce8a2.txt data/version0/c48bdce5.txt data/version0/23e6fa9b.txt data/version0/a2445246.txt data/version0/c274241d.txt
{
  "txid": "8a5d842262f9e4cb964c10a4751564215ee2257983d5ef15b68dae68b6ac9724",
  "inputs": [
    {
      "vin": 0,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 22439000
    },
    {
      "vin": 1,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 10000000
    },
    {
      "vin": 2,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 10000000
    },
    {
      "vin": 3,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 107909
    },
    {
      "vin": 4,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 107909
    },
    {
      "vin": 5,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 107909
    },
    {
      "vin": 6,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 29676273
    },
    {
      "vin": 7,
      "asset": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",
      "satoshi": 5282
    }
  ],
  "outputs": [
    {
      "vout": 1,
      "asset": "ce091c998b83c78bb71a632313ba3760f1763d9cfcffae02258ffa9865a37bd2",
      "satoshi": 22439000
    },
    {
      "vout": 2,
      "asset": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",
      "satoshi": 4808
    }
  ]
}
```

### No version

Verify revealed asset and satoshi for some outputs:

```
$ python verify-elements-commitments.py --tx data/no-version/36d9b0d4.txt --blinded data/no-version/blinders1.json
{
  "txid": "36d9b0d47c09bbb1f5ffc363f89e9deef54fd71ece0c0d94196084b2e0af673e",
  "inputs": [],
  "outputs": [
    {
      "vout": 0,
      "asset": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",
      "satoshi": 6315
    }
  ]
}
```

Verify revealed asset (only) for some outputs:

```
$ python verify-elements-commitments.py --tx data/no-version/36d9b0d4.txt --blinded data/no-version/blinders1asset.json
{
  "txid": "36d9b0d47c09bbb1f5ffc363f89e9deef54fd71ece0c0d94196084b2e0af673e",
  "inputs": [],
  "outputs": [
    {
      "vout": 0,
      "asset": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d"
    }
  ]
}
```

Or only satoshi:

```
$ python verify-elements-commitments.py --tx data/no-version/36d9b0d4.txt --blinded data/no-version/blinders1amount.json
{
  "txid": "36d9b0d47c09bbb1f5ffc363f89e9deef54fd71ece0c0d94196084b2e0af673e",
  "inputs": [],
  "outputs": [
    {
      "vout": 0,
      "satoshi": 6315
    }
  ]
}
```

Verify revealed asset and satoshi for some _inputs_:

```
$ python verify-elements-commitments.py --tx data/no-version/aeaa29a3.txt --blinded data/no-version/blinders2.json --input-txs  data/no-version/36d9b0d4.txt
{
  "txid": "aeaa29a3252a024f49ea22bec4aaf07852de7d46bbae7ca06d347b1015e5d32b",
  "inputs": [
    {
      "vin": 0,
      "asset": "6f0279e9ed041c3d710a9f57d0c02928416460c4b722ae3457a11eec381c526d",
      "satoshi": 6315
    }
  ],
  "outputs": []
}
```

## License

[MIT](LICENSE)
