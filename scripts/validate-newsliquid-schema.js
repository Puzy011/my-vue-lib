const assert = require("assert");
const schema = require("../src/newsliquid/schemas/event.schema.json");
const examples = require("../src/newsliquid/schemas/event.examples.json");

const allowedEventTypes = [
  "OI_SPIKE",
  "OI_CONCENTRATION",
  "WHALE_PNL_START",
];

assert.deepStrictEqual(
  schema.properties.eventType.enum,
  allowedEventTypes,
  "eventType enum does not match expected detector types"
);

assert.strictEqual(
  schema.properties.policy.properties.watchlistOnly.const,
  true,
  "events must remain watchlist-only"
);

const gateRequired =
  schema.properties.policy.properties.executionGate.required;

[
  "requiresStructureConfirmation",
  "rejectOnShortTermOIDivergence",
  "rejectOnRangeRegime",
  "rejectOnTipHigh",
  "rejectOnTipLow",
  "degradeOnCrowdedFunding",
  "degradeOnDailyDoubling",
].forEach((field) => {
  assert(
    gateRequired.includes(field),
    `execution gate is missing required field: ${field}`
  );
});

assert.strictEqual(
  examples.length,
  allowedEventTypes.length,
  "each event type should have one example"
);

examples.forEach((example) => {
  assert(
    allowedEventTypes.includes(example.eventType),
    `unsupported example eventType: ${example.eventType}`
  );
  assert.strictEqual(
    example.policy.watchlistOnly,
    true,
    `${example.eventId} must stay watchlist-only`
  );
  assert(
    example.policy.routeTo.includes("WATCHLIST"),
    `${example.eventId} must route to WATCHLIST`
  );
  assert(
    ["NORMAL", "STRONG", "EXTREME"].includes(example.oiContext.oiStrength),
    `${example.eventId} has invalid oiStrength`
  );
});

console.log("NewsLiquid event schema validation passed.");
