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

Verify revealed asset and satoshi for some outputs:

```
$ python verify-elements-commitments.py --tx data/tx1.txt --blinded data/blinders1.json
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
$ python verify-elements-commitments.py --tx data/tx1.txt --blinded data/blinders1asset.json
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
$ python verify-elements-commitments.py --tx data/tx1.txt --blinded data/blinders1amount.json
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
$ python verify-elements-commitments.py --tx data/tx2.txt --blinded data/blinders2.json --input-txs data/tx1.txt
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
