/**
 * Mirror of classify_oi_strength hard rules (Python source of truth).
 * Keeps JS-side regression for: 减仓禁止标强/极强；增仓窗才计入强度。
 */

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

  if (recentDown || recentDelev || higherDelev || !stillBuilding) {
    return { level: "普通", deleveraging: true };
  }
  if (maxAbs >= 10) return { level: "极强", deleveraging: false };
  if (maxAbs >= 3) return { level: "强", deleveraging: false };
  return { level: "普通", deleveraging: false };
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
  });
});
