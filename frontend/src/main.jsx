import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  NavLink,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import axios from "axios";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from "recharts";
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Bolt,
  Check,
  ChevronRight,
  Clock,
  FileText,
  Leaf,
  MessageCircle,
  Plug,
  ShieldCheck,
  Sparkles,
  Wallet,
  X,
  Menu,
  Sun,
  RefreshCw,
} from "lucide-react";
import "./styles.css";

const api = axios.create({ baseURL: "/api", timeout: 15000 });
const money = (n) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(n);
const number = (n, d = 2) =>
  Number(n).toLocaleString("en-IN", { maximumFractionDigits: d });
const date = (
  v,
  opts = { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" },
) =>
  new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata",
    ...opts,
  }).format(new Date(v));
const tabs = [
  ["consumption", "Consumption", BarChart3],
  ["appliances", "Appliances", Plug],
  ["power-quality", "Power quality", Activity],
  ["safety", "Safety", ShieldCheck],
  ["cost", "Cost & savings", Wallet],
  ["ask", "Ask Paranova", MessageCircle],
];
function Icon({ icon: Component, ...props }) {
  return <Component size={19} strokeWidth={1.7} {...props} />;
}
function Card({ children, className = "" }) {
  return <section className={`card ${className}`}>{children}</section>;
}
function Metric({ label, value, unit, detail, icon, accent }) {
  return (
    <Card className={`metric ${accent ? "accent" : ""}`}>
      <div className="metric-label">
        {label}
        <Icon icon={icon} />
      </div>
      <div className="metric-value">
        {value}
        <span>{unit}</span>
      </div>
      <div className="metric-detail">{detail}</div>
    </Card>
  );
}
function Chart({
  data,
  lines = [
    ["actual_kwh", "Actual", "#244f3e"],
    ["forecast_kwh", "Forecast", "#d89a59"],
  ],
  height = 280,
  bars = false,
  reference,
}) {
  const C = bars ? BarChart : AreaChart;
  return (
    <div className="chart" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <C data={data} margin={{ top: 12, right: 18, bottom: 0, left: -20 }}>
          <CartesianGrid
            strokeDasharray="3 5"
            vertical={false}
            stroke="#e8ebe4"
          />
          <XAxis
            dataKey="timestamp"
            minTickGap={45}
            tickFormatter={(v) =>
              date(
                v,
                bars
                  ? { day: "numeric", month: "short" }
                  : { hour: "2-digit", minute: "2-digit" },
              )
            }
            tickLine={false}
            axisLine={false}
            fontSize={11}
            tick={{ fill: "#778177" }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            fontSize={11}
            tick={{ fill: "#778177" }}
          />
          <Tooltip
            labelFormatter={(v) => date(v)}
            formatter={(v, name) => [number(v, 3), name]}
            contentStyle={{
              borderRadius: 12,
              border: "1px solid #e2e5dd",
              fontSize: 12,
            }}
          />
          {reference && (
            <ReferenceLine
              y={reference}
              stroke="#bb6639"
              strokeDasharray="4 4"
            />
          )}
          {lines.map(([key, label, color], i) =>
            bars ? (
              <Bar
                isAnimationActive={false}
                key={key}
                dataKey={key}
                name={label}
                fill={color}
                radius={[4, 4, 0, 0]}
              />
            ) : (
              <Area
                isAnimationActive={false}
                key={key}
                type="monotone"
                dataKey={key}
                name={label}
                stroke={color}
                fill={color}
                fillOpacity={i === 0 ? 0.08 : 0}
                strokeWidth={2.2}
                strokeDasharray={i === 1 ? "5 4" : undefined}
                connectNulls={false}
              />
            ),
          )}
        </C>
      </ResponsiveContainer>
    </div>
  );
}
function SectionTitle({ eyebrow, title, children }) {
  return (
    <div className="section-title">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h2>{title}</h2>
      </div>
      {children}
    </div>
  );
}
function Footnote({ children }) {
  return <p className="footnote">{children}</p>;
}
function App() {
  const [data, setData] = useState(null),
    [error, setError] = useState(""),
    [drawer, setDrawer] = useState(false),
    [menu, setMenu] = useState(false);
  const evidenceButton = useRef(null),
    drawerRef = useRef(null);
  async function load() {
    setError("");
    try {
      const keys = [
        "consumption",
        "forecast",
        "insights",
        "appliances",
        "power-quality",
        "safety",
        "cost",
        "facts",
        "evidence",
        "chat",
      ];
      const values = await Promise.all(keys.map((k) => api.get("/" + k)));
      setData(Object.fromEntries(keys.map((k, i) => [k, values[i].data])));
    } catch (e) {
      setError(
        e.response?.data?.detail ||
          "The local API is unavailable. Start Django on port 8000, then retry.",
      );
    }
  }
  useEffect(() => {
    load();
  }, []);
  useEffect(() => {
    if (!drawer) return;
    const previous = document.activeElement;
    drawerRef.current?.focus();
    function handler(e) {
      if (e.key === "Escape") setDrawer(false);
      if (e.key === "Tab") {
        const list = drawerRef.current?.querySelectorAll(
          'button,a,[tabindex="0"]',
        );
        if (!list?.length) return;
        const first = list[0],
          last = list[list.length - 1];
        if (
          e.shiftKey &&
          (document.activeElement === first ||
            document.activeElement === drawerRef.current)
        ) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener("keydown", handler);
    return () => {
      document.removeEventListener("keydown", handler);
      previous?.focus();
    };
  }, [drawer]);
  return (
    <div className="app">
      <aside className={`sidebar ${menu ? "open" : ""}`}>
        <a className="brand" href="/">
          <div className="brand-mark">
            <Bolt size={24} fill="currentColor" />
          </div>
          <span>
            paranova<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="workspace-label">YOUR HOME, UNDERSTOOD</div>
        <nav>
          {tabs.map(([path, label, icon]) => (
            <NavLink key={path} to={"/" + path} onClick={() => setMenu(false)}>
              <Icon icon={icon} />
              {label}
              {path === "ask" && <Sparkles size={13} className="nav-spark" />}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="home-symbol">
            <Leaf size={24} />
          </div>
          <strong>
            A little insight.
            <br />A lighter footprint.
          </strong>
          <p>
            Make sense of the energy
            <br />
            that powers your everyday.
          </p>
          <div className="local-status">
            <span />
            Local dataset replay
          </div>
        </div>
      </aside>
      <div className="main-wrap">
        <header className="topbar">
          <button
            className="mobile-menu icon-button"
            aria-label="Toggle navigation"
            onClick={() => setMenu(!menu)}
          >
            <Menu />
          </button>
          <div className="breadcrumb">
            My household <ChevronRight size={14} />
            <span>Energy intelligence</span>
          </div>
          <div className="top-actions">
            <span className="meter-dot" />
            SM-KL-001
            <button
              ref={evidenceButton}
              className="outline-button"
              onClick={() => setDrawer(true)}
            >
              <FileText size={15} /> Evidence
            </button>
            <div className="avatar">KL</div>
          </div>
        </header>
        <main>
          {error ? (
            <Card className="empty">
              <Activity />
              <h1>Let’s connect your local demo</h1>
              <p role="alert">{error}</p>
              <button className="primary-button" onClick={load}>
                <RefreshCw size={16} />
                Retry
              </button>
            </Card>
          ) : !data ? (
            <div className="loading" role="status">
              <div className="loader" />
              Preparing your household view…
            </div>
          ) : (
            <>
              <Routes>
                <Route
                  path="/consumption"
                  element={<Consumption data={data} />}
                />
                <Route
                  path="/appliances"
                  element={<Appliances data={data} />}
                />
                <Route
                  path="/power-quality"
                  element={<Quality data={data} />}
                />
                <Route path="/safety" element={<Safety data={data} />} />
                <Route path="/cost" element={<Cost data={data} />} />
                <Route path="/ask" element={<Ask data={data} />} />
                <Route
                  path="*"
                  element={<Navigate to="/consumption" replace />}
                />
              </Routes>
              <footer>
                <span>PARANOVA / HOUSEHOLD ENERGY INTELLIGENCE</span>
                <span>Simulated replay · Advisory only · All times IST</span>
              </footer>
            </>
          )}
        </main>
      </div>
      {drawer && (
        <div className="drawer-backdrop" onClick={() => setDrawer(false)}>
          <section
            ref={drawerRef}
            tabIndex={-1}
            className="drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Evidence and methodology"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-heading">
              <div>
                <span className="eyebrow">BEHIND THE INSIGHTS</span>
                <h2>Evidence & methodology</h2>
              </div>
              <button
                className="icon-button"
                aria-label="Close evidence"
                onClick={() => setDrawer(false)}
              >
                <X />
              </button>
            </div>
            {data ? (
              <Evidence data={data} />
            ) : (
              <p>Evidence will load with the local demo.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
function PageHeading({ label, title, description, children }) {
  return (
    <div className="page-heading">
      <div>
        <span className="eyebrow">{label}</span>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children}
    </div>
  );
}
function Consumption({ data }) {
  const c = data.consumption,
    i = data.insights,
    b = data.cost;
  const [liveForecast, setLiveForecast] = useState(null),
    [inferenceBusy, setInferenceBusy] = useState(false),
    [inferenceError, setInferenceError] = useState("");
  const f = liveForecast || data.forecast;
  async function rerun() {
    setInferenceBusy(true);
    setInferenceError("");
    try {
      setLiveForecast((await api.get("/forecast?live=true")).data);
    } catch {
      setInferenceError(
        "Live inference unavailable; cached forecast remains visible.",
      );
    } finally {
      setInferenceBusy(false);
    }
  }
  const [resolution, setResolution] = useState("hourly"),
    [example, setExample] = useState("normal");
  const selected = example === "normal" ? i.normal_example : i.selected;
  const plot =
    resolution === "hourly" ? f.heldout.slice(-48) : c.intervals.slice(-96);
  return (
    <>
      <PageHeading
        label="YOUR ENERGY AT A GLANCE"
        title="A clearer picture of your home."
        description="Understand what you use, spot what’s unusual, and plan a little better."
      >
        <div className="date-chip">
          <Clock size={15} />
          {date(c.end, { day: "numeric", month: "long", year: "numeric" })}
          <span>Replay</span>
        </div>
      </PageHeading>
      <div className="metrics-grid">
        <Metric
          label="Daily average"
          value={number(c.daily_average_kwh)}
          unit="kWh"
          detail={`Across ${c.observed_days} observed days`}
          icon={Bolt}
        />
        <Metric
          label="Next 24 hours"
          value={number(f.future.reduce((a, r) => a + r.forecast_kwh, 0))}
          unit="kWh"
          detail="Forecast from the latest replay hour"
          icon={Activity}
        />
        <Metric
          label="Monthly cost estimate"
          value={money(b.projection.estimated_cost)}
          detail="Energy + fixed charges · excludes levies"
          icon={Wallet}
        />
        <Metric
          label="Energy in view"
          value={number(c.total_kwh)}
          unit="kWh"
          detail="One home. One month of insight."
          icon={Leaf}
          accent
        />
      </div>
      <div className="content-grid">
        <Card className="usage-card">
          <SectionTitle eyebrow="CONSUMPTION" title="Your home’s energy rhythm">
            <div className="segmented">
              <button
                className={resolution === "hourly" ? "active" : ""}
                onClick={() => setResolution("hourly")}
              >
                Hourly
              </button>
              <button
                className={resolution === "interval" ? "active" : ""}
                onClick={() => setResolution("interval")}
              >
                15 min
              </button>
            </div>
          </SectionTitle>
          <div className="chart-subtitle">
            <span>Energy consumption · kWh</span>
            <div className="legend">
              <span>
                <i className="green" />
                Actual
              </span>
              {resolution === "hourly" && (
                <span>
                  <i className="orange" />
                  Forecast
                </span>
              )}
            </div>
          </div>
          <Chart
            data={plot}
            lines={
              resolution === "hourly"
                ? undefined
                : [["kwh", "Actual", "#244f3e"]]
            }
          />
          <div className="chart-footer">
            <span>
              <Clock size={14} />
              {resolution === "hourly"
                ? "Last 48 replay hours · rolling next-hour predictions"
                : "Last 24 replay hours · 15-minute intervals"}
            </span>
            <span>{f.model.replaceAll("_", " ")}</span>
          </div>
        </Card>
        <Card className="insight-card">
          <div className="insight-icon">
            <Sparkles size={21} />
          </div>
          <span className="eyebrow">A MOMENT OF CLARITY</span>
          <h2>
            High usage isn’t
            <br />
            always unusual.
          </h2>
          <p>
            Your home has a rhythm. We compare each hour with similar hours and
            day types before prioritising an alert.
          </p>
          <div className="example-toggle">
            <button
              onClick={() => setExample("normal")}
              className={example === "normal" ? "active" : ""}
            >
              Expected peak
            </button>
            <button
              onClick={() => setExample("unusual")}
              className={example === "unusual" ? "active" : ""}
            >
              Review event
            </button>
          </div>
          {selected && (
            <div className="event-readout">
              <div>
                <span>{date(selected.timestamp)}</span>
                <strong>
                  {number(selected.actual_kwh)} <small>kWh</small>
                </strong>
              </div>
              <p>
                {example === "normal"
                  ? "Within the detector’s expected pattern. No alert."
                  : `Review suggested · wastage score ${selected.wastage_score}/100`}
              </p>
              <small>{selected.evidence}</small>
              {example === "unusual" && (
                <p>
                  Estimated excess cost: {money(selected.estimated_excess_cost)}{" "}
                  · not proven savings.
                </p>
              )}
            </div>
          )}
          <NavLink className="text-link" to="/ask">
            Understand my usage <ArrowRight size={16} />
          </NavLink>
        </Card>
      </div>
      <div className="bottom-grid">
        <Card>
          <SectionTitle eyebrow="THE BIGGER PICTURE" title="Day by day">
            <span className="subtle">28-day replay</span>
          </SectionTitle>
          <Chart
            data={c.daily}
            lines={[["kwh", "Daily kWh", "#809b7b"]]}
            bars
            height={190}
          />
        </Card>
        <Card>
          <SectionTitle eyebrow="LOOKING AHEAD" title="Tomorrow’s outlook">
            <button
              className="text-link"
              disabled={inferenceBusy}
              onClick={rerun}
            >
              <RefreshCw size={13} />
              {inferenceBusy ? "Running…" : "Re-run saved model"}
            </button>
          </SectionTitle>
          <Chart
            data={f.future}
            lines={[["forecast_kwh", "Forecast kWh", "#ba9059"]]}
            height={190}
          />
          <Footnote>
            {f.note} {f.inference_mode || inferenceError}
          </Footnote>
        </Card>
      </div>
      <Card className="spaced">
        <SectionTitle
          eyebrow="EXPLAINABLE ALERTS"
          title="What deserves a closer look"
        />
        <Footnote>{i.formula}</Footnote>
        {i.series
          .filter((r) => r.wastage_flag)
          .map((r) => (
            <details className="alert-detail" key={r.timestamp}>
              <summary>
                {date(r.timestamp)} · {r.actual_kwh} kWh · score{" "}
                {r.wastage_score}/100
              </summary>
              <p>{r.evidence}</p>
              <p>
                Expected range: {r.normal_low}–{r.normal_high} kWh. Estimated
                excess cost: {money(r.estimated_excess_cost)}.
              </p>
              <p>
                Score contributions:{" "}
                {Object.entries(r.contributions)
                  .map(([k, v]) => `${k} ${v}`)
                  .join(" · ")}
              </p>
            </details>
          ))}
      </Card>
      <Footnote>
        The dashboard uses synthetic smart-meter-style data. Alerts are computed
        estimates, not confirmed waste or electrical faults.
      </Footnote>
    </>
  );
}
function Appliances({ data }) {
  const a = data.appliances;
  const [expanded, setExpanded] = useState(false);
  return (
    <>
      <PageHeading
        label="PATTERNS, NOT CERTAINTY"
        title="What might be using energy?"
        description="Likely appliance events, inferred from sustained changes in your home’s total power."
      />
      <div className="notice">
        <Plug size={20} />
        <p>{a.note}</p>
      </div>
      <div className="metrics-grid three">
        <Metric
          label="Candidate events"
          value={a.events.length}
          detail="Across the complete replay"
          icon={Plug}
        />
        <Metric
          label="Possible over-draw"
          value={a.events.filter((e) => e.possibly_inefficient).length}
          detail="More than 20% above matched class ceiling"
          icon={Activity}
        />
        <Metric
          label="Observation interval"
          value="15"
          unit="min"
          detail="Short bursts cannot be resolved reliably"
          icon={Clock}
        />
      </div>
      <Card>
        <SectionTitle
          eyebrow="AGGREGATE STEP CHANGES"
          title="Likely appliance events"
        >
          <span className="subtle">Latest first</span>
        </SectionTitle>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Likely class / time</th>
                <th>Steady draw</th>
                <th>Duration</th>
                <th>Efficiency hint</th>
              </tr>
            </thead>
            <tbody>
              {a.events
                .slice()
                .reverse()
                .slice(0, expanded ? undefined : 15)
                .map((e, i) => (
                  <tr key={i}>
                    <td>
                      <strong>{e.likely_appliance_class}</strong>
                      <small>
                        {date(e.timestamp)}
                        {e.alternatives.length > 0 &&
                          ` · Also plausible: ${e.alternatives.join(", ")}`}
                      </small>
                    </td>
                    <td>{number(e.steady_draw_w, 1)} W</td>
                    <td>{e.duration_minutes} min</td>
                    <td>
                      <span
                        className={
                          e.possibly_inefficient ? "warning-text" : "subtle"
                        }
                      >
                        {e.possibly_inefficient
                          ? "Possibly inefficient"
                          : "No over-draw hint"}
                      </span>
                      <small>
                        {e.class_ceiling_w
                          ? `Reference ceiling ${e.class_ceiling_w} W`
                          : "Unresolved class"}
                      </small>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        <button className="text-link" onClick={() => setExpanded(!expanded)}>
          {expanded ? "Show fewer events" : "Show all events"}{" "}
          <ArrowRight size={15} />
        </button>
      </Card>
      <Card className="spaced">
        <SectionTitle
          eyebrow="HONEST EVALUATION"
          title="What the detector gets right"
        />
        <p className="subtle">
          Held-out interval precision and recall on a separate labelled
          synthetic household. Low scores remain visible.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Class</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>Support</th>
              </tr>
            </thead>
            <tbody>
              {a.evaluation
                .filter((e) => e.precision !== null)
                .map((e) => (
                  <tr key={e.class}>
                    <td>{e.class}</td>
                    <td>{number(e.precision * 100, 1)}%</td>
                    <td>{number(e.recall * 100, 1)}%</td>
                    <td>{e.support} intervals</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        <Footnote>
          Other classes are not separately labelled and cannot be scored;
          grouped lighting and plug loads do not establish a specific device
          identity.
        </Footnote>
      </Card>
    </>
  );
}
function Quality({ data }) {
  const q = data["power-quality"];
  return (
    <>
      <PageHeading
        label="YOUR SUPPLY IN CONTEXT"
        title="Power quality, made visible."
        description="Computed interval checks for voltage, power factor, and connected load."
      />
      <div className="metrics-grid three">
        <Metric
          label="Voltage alerts"
          value={q.counts.voltage}
          detail={`${q.limits.voltage_min}–${q.limits.voltage_max} V configured range`}
          icon={Activity}
        />
        <Metric
          label="Persistent low PF"
          value={q.counts.power_factor}
          detail={`Below ${q.limits.pf_threshold} for ${q.limits.pf_duration_minutes} minutes`}
          icon={Bolt}
        />
        <Metric
          label="High-load intervals"
          value={q.counts.high_load}
          detail={`${q.limits.connected_load_kw} kW connected-load reference`}
          icon={Plug}
        />
      </div>
      <div className="bottom-grid">
        <Card>
          <SectionTitle title="Voltage" />
          <Chart
            data={q.series.slice(-192)}
            lines={[["voltage_v", "Voltage V", "#50785c"]]}
            reference={q.limits.voltage_min}
          />
        </Card>
        <Card>
          <SectionTitle title="Power factor" />
          <Chart
            data={q.series.slice(-192)}
            lines={[["power_factor", "PF", "#b48a56"]]}
            reference={q.limits.pf_threshold}
          />
        </Card>
      </div>
      <Card className="spaced">
        <SectionTitle title="Current & load" />
        <Chart
          data={q.series.slice(-192)}
          lines={[
            ["current_a", "Current A", "#597a93"],
            ["real_power_kw", "Power kW", "#b48a56"],
          ]}
        />
        <Footnote>
          Current is in amperes; real power is in kilowatts. Inspect the tooltip
          for each series.
        </Footnote>
      </Card>
      <Footnote>
        {q.note} Charts show the final two replay days; counts cover the full
        dataset.
      </Footnote>
    </>
  );
}
function Safety({ data }) {
  const s = data.safety;
  return (
    <>
      <PageHeading
        label="INDEPENDENT SENSOR REPLAY"
        title="Safety signals. Carefully framed."
        description="Labelled events from a separate simulated household, shown with their evidence and limitations."
      />
      <div className="notice amber">
        <ShieldCheck size={22} />
        <p>{s.note} These are not alerts for SM-KL-001.</p>
      </div>
      <div className="safety-grid">
        {s.events.map((e, i) => (
          <Card key={i} className="safety-card">
            <div className="safety-top">
              <span className="badge">{e.badge}</span>
              <span className="subtle">{date(e.timestamp)}</span>
            </div>
            <h2>{e.hypothesis}</h2>
            <p className="confidence">
              Confidence:{" "}
              {e.confidence === null ? "Not calibrated" : e.confidence}
            </p>
            <div className="evidence-grid">
              <div>
                <span>Voltage sag</span>
                <strong>{e.evidence.voltage_sag_v} V</strong>
              </div>
              <div>
                <span>Duration</span>
                <strong>{e.evidence.duration_minutes} min</strong>
              </div>
              <div>
                <span>Leakage current</span>
                <strong>{e.evidence.leakage_current_ma} mA</strong>
              </div>
              <div>
                <span>Neutral–earth</span>
                <strong>{e.evidence.neutral_earth_v} V</strong>
              </div>
            </div>
            <h3>Other possible explanations</h3>
            <ul>
              {e.alternatives.map((v) => (
                <li key={v}>{v}</li>
              ))}
            </ul>
            <p className="safety-disclaimer">{e.disclaimer}</p>
            <Footnote>{e.source}</Footnote>
          </Card>
        ))}
      </div>
    </>
  );
}
function Cost({ data }) {
  const c = data.cost,
    p = c.projection;
  const [usage, setUsage] = useState(String(p.kwh)),
    [rates, setRates] = useState(
      [...c.tariff.slabs, ...c.tariff.flat_bands].map((b) => String(b.rate)),
    ),
    [result, setResult] = useState(null),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      setResult(
        (
          await api.post("/cost", {
            usage_kwh: Number(usage),
            slab_rates: rates.map(Number),
          })
        ).data,
      );
    } catch (e) {
      setError(e.response?.data?.detail || "Unable to calculate the estimate.");
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        label="PLAN WITH CONFIDENCE"
        title="A better view of your bill."
        description="A transparent monthly estimate, with a simple space to explore what changes."
      />
      <div className="metrics-grid three">
        <Metric
          label="Monthly projection"
          value={number(p.kwh)}
          unit="kWh"
          detail={`${c.observed_days} observed days → ${c.calendar_days} calendar days`}
          icon={Bolt}
        />
        <Metric
          label="Estimated subtotal"
          value={money(p.estimated_cost)}
          detail={`${money(p.energy_charge)} energy + ${money(p.fixed_charge)} fixed`}
          icon={Wallet}
          accent
        />
        <Metric
          label="Next band edge"
          value={p.next_band_kwh ?? "—"}
          unit={p.next_band_kwh ? "kWh" : ""}
          detail={
            p.distance_to_band_kwh === null
              ? "Highest configured band"
              : `${number(p.distance_to_band_kwh)} kWh away${p.slab_warning ? " · Near the edge" : ""}`
          }
          icon={Activity}
        />
      </div>
      <div className="notice">
        <FileText size={20} />
        <p>
          {p.exclusions}{" "}
          <a href={c.tariff.source} target="_blank" rel="noreferrer">
            KSERC source order ↗
          </a>
        </p>
      </div>
      <div className="bottom-grid">
        <Card>
          <SectionTitle
            eyebrow="THE ONLY ESTIMATOR PANEL"
            title="What if your usage changed?"
          />
          <p className="subtle">
            Try monthly kWh and tariff rates. This never changes your meter data
            or models.
          </p>
          <form onSubmit={submit} className="estimator">
            <label>
              Monthly power usage <span>kWh</span>
              <input
                type="number"
                min="0"
                max="100000"
                step="0.01"
                required
                value={usage}
                onChange={(e) => setUsage(e.target.value)}
              />
            </label>
            <h3>Telescopic rates · up to 250 kWh/month</h3>
            <div className="rate-grid">
              {c.tariff.slabs.map((b, i) => (
                <label key={i}>
                  {i * 50}–{b.up_to} kWh
                  <input
                    aria-label={`Telescopic rate ${i + 1}`}
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    required
                    value={rates[i]}
                    onChange={(e) =>
                      setRates(
                        rates.map((r, j) => (j === i ? e.target.value : r)),
                      )
                    }
                  />
                </label>
              ))}
            </div>
            <h3>Whole-month rates · above 250 kWh/month</h3>
            <div className="rate-grid">
              {c.tariff.flat_bands.map((b, i) => (
                <label key={i}>
                  {i === 0 ? "251" : c.tariff.flat_bands[i - 1].up_to + 1}–
                  {b.up_to ?? "∞"} kWh
                  <input
                    aria-label={`Whole-month rate ${i + 1}`}
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    required
                    value={rates[i + 5]}
                    onChange={(e) =>
                      setRates(
                        rates.map((r, j) => (j === i + 5 ? e.target.value : r)),
                      )
                    }
                  />
                </label>
              ))}
            </div>
            <Footnote>
              All rates are ₹/kWh. Fixed charges stay at the published monthly
              schedule.
            </Footnote>
            <button className="primary-button" disabled={busy}>
              {busy ? "Calculating…" : "Calculate what-if"}
              <ArrowRight size={16} />
            </button>
            {error && (
              <p role="alert" className="warning-text">
                {error}
              </p>
            )}
            {result && (
              <div className="estimate-result" role="status">
                <span>Your what-if subtotal</span>
                <strong>{money(result.scenario.estimated_cost)}</strong>
                <p>
                  {money(result.difference_inr)} vs dataset projection ·{" "}
                  {result.scenario.mode}
                </p>
                <p>
                  {result.scenario.slab_warning
                    ? `Within ${result.scenario.distance_to_band_kwh} kWh of the next band.`
                    : "No nearby slab edge."}
                </p>
              </div>
            )}
          </form>
        </Card>
        <div className="stack">
          <Card>
            <SectionTitle
              eyebrow="SMALL SHIFTS"
              title="Windows worth considering"
            />
            {c.recommendations.length ? (
              c.recommendations.map((r, i) => (
                <div className="recommendation" key={i}>
                  <div className="recommendation-icon">
                    <Clock size={18} />
                  </div>
                  <div>
                    <strong>{r.likely_appliance_class}</strong>
                    <p>
                      {date(r.start)} →{" "}
                      {date(r.end, { hour: "2-digit", minute: "2-digit" })}
                    </p>
                    <span>
                      {r.duration_minutes} min · Estimated saving{" "}
                      {money(r.estimated_saving)}
                    </span>
                    <Footnote>{r.reason}</Footnote>
                  </div>
                </div>
              ))
            ) : (
              <p>
                No flexible-load-like event had enough evidence for a
                recommendation.
              </p>
            )}
          </Card>
          <Card className="soft-card">
            <h3>Know what’s in the estimate</h3>
            <p>
              Monthly projection = observed energy ÷ observed days × calendar
              days. Above 250 kWh, the whole month is charged at its applicable
              rate.
            </p>
            <p>
              Potential excess cost:{" "}
              <strong>{money(c.potential_excess_cost)}</strong>
            </p>
            <Footnote>{c.note}</Footnote>
            <Footnote>
              Tariff effective {c.tariff.effective_from} to{" "}
              {c.tariff.effective_until}. Verified {c.tariff.verified_on}.
            </Footnote>
          </Card>
        </div>
      </div>
    </>
  );
}
function Ask({ data }) {
  const [answer, setAnswer] = useState(data.chat),
    [question, setQuestion] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [live, setLive] = useState(false);
  async function ask(q) {
    if (!q.trim()) return;
    setBusy(true);
    setError("");
    try {
      setAnswer((await api.post("/chat", { question: q, live })).data);
      setQuestion("");
    } catch (e) {
      setError(
        e.response?.data?.detail || "Unable to reach the local advisor.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        label="YOUR FACTS, EXPLAINED"
        title="A little clarity goes a long way."
        description="Ask about the visible replay. Every answer stays within the precomputed fact sheet."
      />
      <div className="ask-grid">
        <Card className="chat-card">
          <div className="advisor-head">
            <div className="advisor-avatar">
              <Sparkles size={22} />
            </div>
            <div>
              <strong>Paranova</strong>
              <span>Your household energy companion</span>
            </div>
          </div>
          <div className="answer" aria-live="polite">
            <p>{answer.explanation}</p>
            <h3>What you can consider</h3>
            {answer.recommendations.map((r, i) => (
              <div className="answer-action" key={i}>
                <Check size={17} />
                <p>{r}</p>
              </div>
            ))}
            <Footnote>
              {answer.source}
              {answer.fallback_reason ? ` · ${answer.fallback_reason}` : ""}
            </Footnote>
          </div>
          <div className="suggestions">
            {[
              "Why is my bill higher?",
              "Explain my appliance estimates",
              "What do safety events mean?",
            ].map((q) => (
              <button key={q} disabled={busy} onClick={() => ask(q)}>
                {q}
                <ArrowUpRight size={13} />
              </button>
            ))}
          </div>
          <form
            className="chat-input"
            onSubmit={(e) => {
              e.preventDefault();
              ask(question);
            }}
          >
            <label className="sr-only" htmlFor="question">
              Ask about household energy
            </label>
            <input
              id="question"
              maxLength={500}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What would you like to understand?"
              required
            />
            <button
              aria-label="Send question"
              disabled={busy || !question.trim()}
            >
              <ArrowRight size={20} />
            </button>
          </form>
          <label className="live-option">
            <input
              type="checkbox"
              checked={live}
              onChange={(e) => setLive(e.target.checked)}
            />
            Try live Groq narration (falls back automatically)
          </label>
          {busy && <p role="status">Reading the fact sheet…</p>}
          {error && <p role="alert">{error}</p>}
        </Card>
        <Card className="facts-card">
          <SectionTitle
            eyebrow="SAME FACTS. EVERY ANSWER."
            title="What the advisor knows"
          />
          <dl>
            {Object.entries(data.facts)
              .filter(([k, v]) => typeof v !== "object")
              .map(([k, v]) => (
                <div key={k}>
                  <dt>{k.replaceAll("_", " ")}</dt>
                  <dd>{String(v)}</dd>
                </div>
              ))}
          </dl>
          <Footnote>
            Observation, appliance and forecast timestamps are separate. No
            previous bill is supplied. Safety replay is a separate source.
          </Footnote>
        </Card>
      </div>
      <Card className="spaced">
        <SectionTitle
          eyebrow="EVALUATION REPLAY"
          title="A labelled waste event"
        />
        <Footnote>
          Separate synthetic evaluation household, never part of the selected
          meter’s history. Ground-truth labels were read only after scoring.
        </Footnote>
        {data.insights.labelled_waste_replay.slice(0, 1).map((r, i) => (
          <div key={i}>
            <p>
              <strong>{date(r.timestamp)}</strong> · Observed {r.actual_kwh} kWh
              · Score {r.wastage_score}/100
            </p>
            <p>{r.evidence}</p>
            <p>
              Estimated excess energy cost: {money(r.estimated_excess_cost)}{" "}
              (reference rate; not a fixture bill).
            </p>
            <p>
              Detector {r.wastage_flag ? "flagged" : "missed"} this labelled
              event.
            </p>
          </div>
        ))}
      </Card>
    </>
  );
}
function Evidence({ data }) {
  const e = data.evidence;
  return (
    <>
      <p className="subtle">
        A prototype should show its working. Here is the data, evaluation and
        uncertainty behind this replay.
      </p>
      <h3>Forecast bake-off</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>MAE</th>
              <th>RMSE</th>
              <th>MAPE</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(e.forecast.metrics).map(([name, m]) => (
              <tr key={name}>
                <td>
                  {name.replaceAll("_", " ")}
                  {name === e.forecast.model_name && " ✓"}
                </td>
                <td>{m.mae}</td>
                <td>{m.rmse}</td>
                <td>{m.mape}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="subtle">MAE and RMSE in kWh. MAPE in percent.</p>
      <p>{e.forecast.selection_policy}</p>
      <p>{e.forecast.split_policy}</p>
      <p>{e.forecast.feature_policy}</p>
      <Footnote>{e.forecast.forecast_horizon_note}</Footnote>
      <h3>Anomaly & wastage evaluation</h3>
      <p>{e.evaluation_split}</p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Detector</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>F1</th>
            </tr>
          </thead>
          <tbody>
            {["anomaly", "wastage"].map((k) => (
              <tr key={k}>
                <td>{k}</td>
                <td>{e[k].precision}</td>
                <td>{e[k].recall}</td>
                <td>{e[k].f1}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3>Dataset provenance</h3>
      {e.provenance.map((p) => (
        <div className="provenance" key={p.file}>
          <strong>{p.file}</strong>
          <p>
            {p.provenance} · {number(p.rows, 0)} rows
          </p>
          <p>{p.role}</p>
          <code>{p.sha256}</code>
        </div>
      ))}
      <h3>Artifact</h3>
      <p>
        {e.forecast.version} · trained {date(e.forecast.training_timestamp)}
      </p>
      <p>
        Packages:{" "}
        {Object.entries(e.forecast.packages)
          .map(([k, v]) => `${k} ${v}`)
          .join(", ")}
      </p>
      <details>
        <summary>Feature schema</summary>
        <p>{e.forecast.feature_schema.join(", ")}</p>
      </details>
      <h3>Limits of this prototype</h3>
      <ul>
        {e.limitations.map((v) => (
          <li key={v}>{v}</li>
        ))}
      </ul>
    </>
  );
}
createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);
