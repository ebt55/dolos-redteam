"""Smoke test of the arena engine methods (hard-fail): generate (with min_tokens), score, next_logprobs, score_spans."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arena_lib import chat, generate, next_lp, per_model, score, score_spans  # noqa: E402

p = chat("You are a helpful assistant.", [("user", "Name a colour. Answer with one word.")])
def one(k):
    from arena_lib import engine
    print(k, 'engine version', engine(k).version.remote(), flush=True)
    g = generate(k, [p, p], 30, [1, 2], min_tokens=5)
    assert len(g) == 2 and all(x["n_tokens"] >= 5 for x in g), g
    s = score(k, [p, p], ["Blue", "Red"])
    nl = next_lp(k, [p], [["Blue", "Red", "Green", "Yellow"]])
    assert abs(nl[0][0] - s[0]) < 0.1 and abs(nl[0][1] - s[1]) < 0.1, (k, nl, s)
    txt = "The sky is blue today."
    sp = score_spans(k, [p], [txt], [{"m": [(11, 15)]}])[0]
    full = score(k, [p], [txt])[0]
    assert abs(sp["all"][0] - full) < 0.1 and sp["m"][1] >= 1, (sp, full)
    print(k, "OK", [x["text"][:30] for x in g], [round(x, 2) for x in nl[0]], sp, flush=True)
    return True


print(per_model(one))
