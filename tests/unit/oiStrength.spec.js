/**
 * Mirror of classify_oi_strength hard rules (Python source of truth).
 * Keeps JS-side regression for: 减仓禁止标强/极强；增仓窗才计入强度；5m 极强阈。
 */

const OI_STRONG = 3.0;
const OI_EXTREME = 10.0;
const OI_EXTREME_5M = 5.0;

function classifyOiStrength(oiChanges, quadrants) {
  const buildQs = ["Q1_涨价增仓", "Q2_跌价增仓"];
  const delevQs = ["Q3_涨价减仓", "Q4_跌价减仓"];
  const vals = {
    "5m": oiChanges["5m"],
    "15m": oiChanges["15m"],
    "1h": oiChanges["1h"],
    "4h": oiChanges["4h"],
  };
  const recentDown =
    vals["15m"] != null && vals["15m"] < 0 && vals["1h"] != null && vals["1h"] < 0;
  const qRecent = quadrants["15m"] || quadrants["1h"] || "";
  const recentDelev = delevQs.includes(qRecent);
  const higherDelev =
    delevQs.includes(quadrants["1h"]) && delevQs.includes(quadrants["4h"]);
  const stillBuilding =
    !recentDown &&
    !recentDelev &&
    ((vals["15m"] > 0 && buildQs.includes(quadrants["15m"])) ||
      (vals["1h"] > 0 && buildQs.includes(quadrants["1h"])));

  const absBuild = ["15m", "1h", "4h"]
    .map((k) => vals[k])
    .filter((v, i) => {
      const k = ["15m", "1h", "4h"][i];
      return v != null && v > 0 && buildQs.includes(quadrants[k]);
    });
  const maxAbs = absBuild.length ? Math.max(...absBuild) : 0;
  const v5 = vals["5m"];
  const v5Build = v5 != null && v5 > 0 && buildQs.includes(quadrants["5m"]);

  if (recentDown || recentDelev || higherDelev || !stillBuilding) {
    return { level: "普通", deleveraging: true, buildup: false };
  }
  const extreme =
    maxAbs >= OI_EXTREME || (v5Build && Math.abs(v5) >= OI_EXTREME_5M);
  if (extreme) return { level: "极强", deleveraging: false, buildup: true };
  if (maxAbs >= OI_STRONG) return { level: "强", deleveraging: false, buildup: true };
  return { level: "普通", deleveraging: false, buildup: true };
}

describe("OI strength grading", () => {
  it("never marks deleveraging as 强/极强 even with large |ΔOI|", () => {
    const r = classifyOiStrength(
      { "5m": 0.54, "15m": 0.249, "1h": -1.798, "4h": -9.779 },
      {
        "5m": "Q1_涨价增仓",
        "15m": "Q2_跌价增仓",
        "1h": "Q4_跌价减仓",
        "4h": "Q3_涨价减仓",
        "24h": "Q4_跌价减仓",
      }
    );
    expect(r.level).toBe("普通");
    expect(r.deleveraging).toBe(true);
  });

  it("marks true short buildup spike as 极强", () => {
    const r = classifyOiStrength(
      { "5m": 2.0, "15m": 6.4, "1h": 12.0, "4h": 41.6 },
      {
        "5m": "Q2_跌价增仓",
        "15m": "Q2_跌价增仓",
        "1h": "Q2_跌价增仓",
        "4h": "Q2_跌价增仓",
        "24h": "Q2_跌价增仓",
      }
    );
    expect(r.level).toBe("极强");
    expect(r.buildup).toBe(true);
  });

  it("marks 5m same-direction buildup >=5% as 极强", () => {
    const r = classifyOiStrength(
      { "5m": 5.2, "15m": 2.1, "1h": 1.5, "4h": 2.0 },
      {
        "5m": "Q1_涨价增仓",
        "15m": "Q1_涨价增仓",
        "1h": "Q1_涨价增仓",
        "4h": "Q1_涨价增仓",
        "24h": "Q1_涨价增仓",
      }
    );
    expect(r.level).toBe("极强");
  });

  it("marks mid buildup as 强", () => {
    const r = classifyOiStrength(
      { "5m": 1.0, "15m": 4.2, "1h": 3.5, "4h": 2.0 },
      {
        "5m": "Q1_涨价增仓",
        "15m": "Q1_涨价增仓",
        "1h": "Q1_涨价增仓",
        "4h": "Q1_涨价增仓",
        "24h": "Q1_涨价增仓",
      }
    );
    expect(r.level).toBe("强");
  });
});
