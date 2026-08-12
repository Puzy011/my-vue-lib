const schema = require("../../src/newsliquid/schemas/event.schema.json");
const examples = require("../../src/newsliquid/schemas/event.examples.json");

describe("newsliquid event schema", () => {
  it("defines the expected event types", () => {
    expect(schema.properties.eventType.enum).toEqual([
      "OI_SPIKE",
      "OI_CONCENTRATION",
      "WHALE_PNL_START",
    ]);
  });

  it("locks events to watchlist-only routing", () => {
    expect(schema.properties.policy.properties.watchlistOnly.const).toBe(true);
    expect(
      schema.properties.policy.properties.routeTo.items.enum.includes("WATCHLIST")
    ).toBe(true);
  });

  it("includes execution gates that block direct auto-entry", () => {
    const gate =
      schema.properties.policy.properties.executionGate.required;

    expect(gate).toEqual(
      expect.arrayContaining([
        "requiresStructureConfirmation",
        "rejectOnShortTermOIDivergence",
        "rejectOnRangeRegime",
        "rejectOnTipHigh",
        "rejectOnTipLow",
        "degradeOnCrowdedFunding",
        "degradeOnDailyDoubling",
      ])
    );
  });

  it("ships examples for every event type", () => {
    expect(examples).toHaveLength(3);
    expect(examples.map((example) => example.eventType)).toEqual([
      "OI_SPIKE",
      "OI_CONCENTRATION",
      "WHALE_PNL_START",
    ]);
  });

  it("ensures examples remain watchlist-only and include OI strength", () => {
    examples.forEach((example) => {
      expect(example.policy.watchlistOnly).toBe(true);
      expect(example.policy.routeTo).toContain("WATCHLIST");
      expect(["NORMAL", "STRONG", "EXTREME"]).toContain(
        example.oiContext.oiStrength
      );
      expect(example.oiContext).toEqual(
        expect.objectContaining({
          changePct5m: expect.any(Number),
          changePct15m: expect.any(Number),
          changePct1h: expect.any(Number),
          changePct4h: expect.any(Number),
        })
      );
    });
  });
});
