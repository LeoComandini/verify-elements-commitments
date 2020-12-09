import argparse
import json
import logging
import sys

import wallycore as wally

b2h = lambda b: wally.hex_from_bytes(b)
h2b = lambda h: wally.hex_to_bytes(h)
b2h_rev = lambda b: b2h(b[::-1])
h2b_rev = lambda h: h2b(h)[::-1]

def err(s):
    logging.error(s)
    sys.exit(1)

def parse_tx_file(file):
    with file as f:
        try:
            return wally.tx_from_hex(f.read().strip(), wally.WALLY_TX_FLAG_USE_WITNESS | wally.WALLY_TX_FLAG_USE_ELEMENTS)
        except ValueError:
            err("Invalid transaction")

def parse_uint256_hex(h):
    try:
        b = h2b_rev(h)
        if len(b) != 32:
            err("Invalid length")
        return b
    except (ValueError, TypeError):
        err("Invalid hex value")

def parse_commitment_hex(h):
    try:
        b = h2b(h)
        if len(b) != 33:
            err("Invalid length")
        return b
    except (ValueError, TypeError):
        err("Invalid hex value")

def parse_int(i, max):
    try:
        i = int(i)
        if i <= 0 or i > max:
            err("Invalid range")
        return i
    except (ValueError, TypeError):
        err("Invalid int")

def parse_idx(i):
    return parse_int(i, max=2**32-1)

def parse_sat(i):
    return parse_int(i, max=21*10**14)

def parse_blinded_element(e):
    valid_key_sets = [
        {"asset_id_hex", "asset_blinder_hex", "amount_satoshi", "amount_blinder_hex"},
        {"asset_id_hex", "asset_blinder_hex"},
        {"amount_satoshi", "amount_blinder_hex", "asset_commitment_hex"},
    ]
    if not isinstance(e, dict):
        err("Should be a dict")
    if set(e.keys()) not in valid_key_sets:
        err("Invalid keys")

    if "asset_id_hex" in e:
        asset_commitment_bin = wally.asset_generator_from_bytes(parse_uint256_hex(e["asset_id_hex"]), parse_uint256_hex(e["asset_blinder_hex"]))
    else:
        asset_commitment_bin = parse_commitment_hex(e["asset_commitment_hex"])

    if "amount_satoshi" in e:
        amount_commitment_bin = wally.asset_value_commitment(parse_sat(e["amount_satoshi"]), parse_uint256_hex(e["amount_blinder_hex"]), asset_commitment_bin)
    else:
        amount_commitment_bin = None

    return {
        "asset_id_hex": e.get("asset_id_hex"),
        "asset_commitment_bin": asset_commitment_bin,
        "amount_satoshi": e.get("amount_satoshi"),
        "amount_commitment_bin": amount_commitment_bin,
    }

def reorder_elements_v0(l, key):
    if len(l) == 0:
        return l

    valid_key_sets = [
        {"asset_id", "assetblinder", "satoshi", "amountblinder", key},
    ]
    for e in l:
        if not isinstance(e, dict):
            err("Should be a dict")
        if set(e.keys()) not in valid_key_sets:
            err("Invalid keys")

    indexes = {e[key] for e in l}
    if len(l) != len(indexes):
        err("Repeated indexes")
    return [next((e for e in l if e[key] == i), {key: i}) for i in range(max(indexes) + 1)]

def parse_blinded_element_v0(e):
    asset_commitment_bin = None
    amount_commitment_bin = None
    if len(e.keys()) == 5:
        asset_commitment_bin = wally.asset_generator_from_bytes(parse_uint256_hex(e["asset_id"]), parse_uint256_hex(e["assetblinder"]))
        amount_commitment_bin = wally.asset_value_commitment(parse_sat(e["satoshi"]), parse_uint256_hex(e["amountblinder"]), asset_commitment_bin)

    return {
        "asset_id_hex": e.get("asset_id"),
        "asset_commitment_bin": asset_commitment_bin,
        "amount_satoshi": e.get("satoshi"),
        "amount_commitment_bin": amount_commitment_bin,
    }

def parse_json_no_version(j):
    if set(j.keys()) != {"inputs", "outputs"}:
        err("Invalid keys")
    if not isinstance(j["inputs"], list):
        err("Should be a list")
    if not isinstance(j["outputs"], list):
        err("Should be a list")

    inputs_unblinded = {vin: parse_blinded_element(e) for vin, e in enumerate(j["inputs"])}
    outputs_unblinded = {vout: parse_blinded_element(e) for vout, e in enumerate(j["outputs"])}

    return inputs_unblinded, outputs_unblinded

def parse_json_v0(j):
    if set(j.keys()) != {"version", "inputs", "outputs", "txid", "type"}:
        err("Invalid keys")
    if not isinstance(j["inputs"], list):
        err("Should be a list")
    if not isinstance(j["outputs"], list):
        err("Should be a list")

    inputs_unblinded = {vin: parse_blinded_element_v0(e) for vin, e in enumerate(reorder_elements_v0(j["inputs"], key="vin"))}
    outputs_unblinded = {vout: parse_blinded_element_v0(e) for vout, e in enumerate(reorder_elements_v0(j["outputs"], key="vout"))}

    return inputs_unblinded, outputs_unblinded

def parse_blinded_file(file):
    with file as f:
        j = json.load(file)
        if not isinstance(j, dict):
            err("Should be a dict")
        version = j.get("version")
        if version is None:
            return parse_json_no_version(j)
        if version == 0:
            return parse_json_v0(j)
        err("Unsupported version")

def parse_input_txs(input_tx_files):
    input_txs_map = {}
    for input_tx_file in input_tx_files or []:
        input_tx = parse_tx_file(input_tx_file)
        txid = wally.sha256d(wally.tx_to_bytes(input_tx, 0))
        input_txs_map[bytes(txid)] = input_tx
    return input_txs_map

def main():
    parser = argparse.ArgumentParser(description="Verify Elements Commitments")
    parser.add_argument("--tx", type=argparse.FileType("r"), required=True)
    parser.add_argument("--blinded", type=argparse.FileType("r"), required=True)
    parser.add_argument("--input-txs", type=argparse.FileType("r"), nargs="+")

    args = parser.parse_args()
    tx = parse_tx_file(args.tx)
    inputs_unblinded, outputs_unblinded = parse_blinded_file(args.blinded)
    input_txs_map = parse_input_txs(args.input_txs)

    ret = {
        "txid": b2h_rev(wally.sha256d(wally.tx_to_bytes(tx, 0))),
        "inputs": [],
        "outputs": [],
    }

    for inp_idx in range(wally.tx_get_num_inputs(tx)):
        input_unblinded = inputs_unblinded.get(inp_idx)
        if not input_unblinded:
            continue
        prev_txid = wally.tx_get_input_txhash(tx, inp_idx)
        prev_vout = wally.tx_get_input_index(tx, inp_idx)
        prev_tx = input_txs_map.get(bytes(prev_txid))
        if not prev_tx:
            continue
        asset_commitment_bin = wally.tx_get_output_asset(prev_tx, prev_vout)
        amount_commitment_bin = wally.tx_get_output_value(prev_tx, prev_vout)
        if asset_commitment_bin != input_unblinded["asset_commitment_bin"]:
            continue
        i = {"vin": inp_idx}
        # TODO: fill also if unblinded
        if input_unblinded.get("asset_id_hex"):
            i["asset"] = input_unblinded["asset_id_hex"]
        if amount_commitment_bin == input_unblinded["amount_commitment_bin"]:
            i["satoshi"] = input_unblinded["amount_satoshi"]

        ret["inputs"].append(i)

    for out_idx in range(wally.tx_get_num_outputs(tx)):
        output_unblinded = outputs_unblinded.get(out_idx)
        if not output_unblinded:
            continue
        asset_commitment_bin = wally.tx_get_output_asset(tx, out_idx)
        amount_commitment_bin = wally.tx_get_output_value(tx, out_idx)
        if asset_commitment_bin != output_unblinded["asset_commitment_bin"]:
            continue
        o = {"vout": out_idx}
        # TODO: fill also if unblinded
        if output_unblinded.get("asset_id_hex"):
            o["asset"] = output_unblinded["asset_id_hex"]
        if amount_commitment_bin == output_unblinded["amount_commitment_bin"]:
            o["satoshi"] = output_unblinded["amount_satoshi"]

        ret["outputs"].append(o)

    print(json.dumps(ret, indent=2))


if __name__ == "__main__":
    main()
