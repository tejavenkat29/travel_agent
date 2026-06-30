import type { TravelSummary } from "../lib/types";

function money(currency: string, amount: number): string {
  return `${currency} ${amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

const MODE_ICON: Record<string, string> = { flight: "✈️", train: "🚆", bus: "🚌" };

/** Renders a structured TravelSummary as scannable cards (vs. raw markdown). */
export function TripPlan({ summary: s }: { summary: TravelSummary }) {
  const cur = s.currency;
  const t = s.transport;
  const available = t?.options.filter((o) => o.available && o.total_price != null) ?? [];

  return (
    <div className="plan">
      {/* Header */}
      <div className="plan-head">
        <h2>🌍 {s.destination || "Your trip"}</h2>
        <div className="plan-meta">
          {s.source && <span>from {s.source}</span>}
          <span>{s.num_days} day(s)</span>
          <span>{s.travelers} traveler(s)</span>
          {s.budget?.user_budget != null && (
            <span>budget {money(cur, s.budget.user_budget)}</span>
          )}
        </div>
      </div>

      <div className="plan-grid">
        {/* Transport */}
        {t && (
          <section className="pcard">
            <h3>🚆 Getting There</h3>
            {available.length === 0 && <p className="muted">No options found.</p>}
            {available.map((o) => (
              <div key={o.mode} className="mode-row">
                <div className="mode-head">
                  <span className="mode-name">
                    {MODE_ICON[o.mode]} {o.mode[0].toUpperCase() + o.mode.slice(1)}
                  </span>
                  <span className="mode-price">
                    {o.total_price != null ? money(o.currency, o.total_price) : "—"}
                    {o.duration_hours ? ` · ${o.duration_hours}h` : ""}
                  </span>
                </div>
                {o.fare_classes.length > 0 && (
                  <div className="fare-chips">
                    {o.fare_classes.map((fc) => (
                      <span key={fc.name} className="chip">
                        {fc.name} {money(o.currency, fc.price_per_person)}
                      </span>
                    ))}
                  </div>
                )}
                {o.booking_apps.length > 0 && (
                  <div className="apps">Book: {o.booking_apps.slice(0, 3).join(", ")}</div>
                )}
              </div>
            ))}
            {t.options
              .filter((o) => !o.available && o.note)
              .map((o) => (
                <p key={o.mode} className="note">⚠️ {o.note}</p>
              ))}
            {t.recommended && (
              <p className="reco">
                ✅ Recommended: <b>{t.recommended.mode}</b> —{" "}
                {t.recommended.total_price != null
                  ? money(t.recommended.currency, t.recommended.total_price)
                  : ""}
              </p>
            )}
            <p className="disclaimer">ℹ️ {t.disclaimer}</p>
          </section>
        )}

        {/* Hotels — suggestions for the location */}
        {(s.hotel_options?.length || s.hotel) && (
          <section className="pcard">
            <h3>🏨 Hotels</h3>
            {(s.hotel_options?.length ? s.hotel_options : s.hotel ? [s.hotel] : []).map(
              (h) => {
                const isReco = s.hotel && h.name === s.hotel.name;
                return (
                  <div key={h.name} className="mode-row">
                    <div className="mode-head">
                      <span className="mode-name">
                        {h.name} {isReco && <span className="reco-star">⭐</span>}
                      </span>
                      <span className="mode-price">
                        {money(h.currency, h.total_price)}
                      </span>
                    </div>
                    <div className="muted">
                      {h.rating ? `${h.rating}★` : ""}
                      {h.area ? ` · ${h.area}` : ""} ·{" "}
                      {money(h.currency, h.nightly_rate)}/night × {h.nights}
                    </div>
                  </div>
                );
              },
            )}
            <div className="apps">Book: OYO, MakeMyTrip, Booking.com</div>
          </section>
        )}

        {/* Weather */}
        {s.weather && (
          <section className="pcard">
            <h3>🌤️ Weather & Packing</h3>
            <div className="big">
              {s.weather.forecast.condition} ·{" "}
              {Math.round(s.weather.forecast.temp_low_c)}–
              {Math.round(s.weather.forecast.temp_high_c)}°C
            </div>
            <div className="muted">🗓️ {s.weather.best_time_to_visit}</div>
            {s.weather.clothing_suggestions.length > 0 && (
              <ul className="bullets">
                {s.weather.clothing_suggestions.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            )}
          </section>
        )}

        {/* Budget */}
        {s.budget && (
          <section className="pcard">
            <h3>💰 Budget</h3>
            <table className="budget-table">
              <tbody>
                {s.budget.breakdown.line_items.map((li) => (
                  <tr key={li.category}>
                    <td>{li.category}</td>
                    <td className="amt">{money(cur, li.amount)}</td>
                  </tr>
                ))}
                <tr className="total">
                  <td>Total</td>
                  <td className="amt">{money(cur, s.budget.total_cost)}</td>
                </tr>
              </tbody>
            </table>
            {s.budget.within_budget != null && (
              <span className={`badge ${s.budget.within_budget ? "ok" : "over"}`}>
                {s.budget.within_budget ? "✅ Within budget" : "⚠️ Over budget"}
              </span>
            )}
          </section>
        )}
      </div>

      {/* Recommendations */}
      {s.recommendations.length > 0 && (
        <section className="pcard wide">
          <h3>💡 Recommendations</h3>
          <ul className="bullets">
            {s.recommendations.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </section>
      )}

      {/* Itinerary */}
      {s.daily_itinerary.length > 0 && (
        <section className="pcard wide">
          <h3>🗓️ Daily Itinerary</h3>
          <div className="days">
            {s.daily_itinerary.map((d) => (
              <div key={d.day} className="day">
                <div className="day-title">Day {d.day} — {d.title}</div>
                <ul className="bullets">
                  {d.activities.map((a) => (
                    <li key={a}>{a}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
