import { useState } from 'react';
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  BarChart3,
  Check,
  ChevronDown,
  CircleAlert,
  Database,
  FileCode2,
  Gauge,
  GitBranch,
  Layers3,
  Menu,
  MoveUpRight,
  Network,
  PanelTop,
  Play,
  ShieldCheck,
  Sparkles,
  X,
} from 'lucide-react';

type MetricGroup = 'all' | 'load' | 'flow' | 'diagnostic';

type Metric = {
  name: string;
  formula: string;
  description: string;
  group: Exclude<MetricGroup, 'all'>;
  tag: 'OBSERVED' | 'DERIVED' | 'FLAGGED';
  accent: string;
};

const metrics: Metric[] = [
  {
    name: 'Total System Load',
    formula: 'CBP custody + HHS care',
    description: 'The reported stock of children recorded across the two care locations on a reporting date.',
    group: 'load',
    tag: 'DERIVED',
    accent: 'orange',
  },
  {
    name: 'Net Daily Intake',
    formula: 'Transfers − discharges',
    description: 'An HHS flow balance. Positive values signal that incoming transfers exceeded discharges.',
    group: 'flow',
    tag: 'DERIVED',
    accent: 'blue',
  },
  {
    name: 'Care Load Growth Rate',
    formula: 'Δ total load ÷ prior load',
    description: 'Day-over-day percentage change, calculated across valid reporting observations.',
    group: 'load',
    tag: 'DERIVED',
    accent: 'violet',
  },
  {
    name: 'Backlog Indicator',
    formula: '7-observation persistence rule',
    description: 'Positive seven-observation net flow sum with at least four positive observations.',
    group: 'diagnostic',
    tag: 'FLAGGED',
    accent: 'green',
  },
  {
    name: 'Rolling Averages',
    formula: '7 / 14 reporting observations',
    description: 'Trailing means for load and net flow, with no silent zero-filling across missing dates.',
    group: 'load',
    tag: 'DERIVED',
    accent: 'orange',
  },
  {
    name: 'Volatility Index',
    formula: '100 × σ(Δ load) ÷ mean load',
    description: 'Scale-normalized variability in reported load changes. It is not clinical acuity.',
    group: 'diagnostic',
    tag: 'DERIVED',
    accent: 'violet',
  },
  {
    name: 'Backlog Accumulation Rate',
    formula: '7-observation mean net flow',
    description: 'Average care-pressure proxy per reporting observation. Positive means accumulation.',
    group: 'flow',
    tag: 'DERIVED',
    accent: 'blue',
  },
  {
    name: 'Discharge Offset Ratio',
    formula: 'Discharges ÷ transfers',
    description: 'A ratio of one means discharges numerically offset transfers during the observation.',
    group: 'flow',
    tag: 'DERIVED',
    accent: 'green',
  },
];

const workflow = [
  ['01', 'Ingest & audit', 'Preserve the raw source. Record schema, checksum, coverage, and source-format findings.'],
  ['02', 'Clean & validate', 'Parse dates and counts, remove only fully blank rows, and publish review flags.'],
  ['03', 'Build metrics', 'Calculate the tested KPI layer once so notebooks and dashboard share the same truth.'],
  ['04', 'Explore time', 'Separate reporting observations from calendar days. Aggregate flows and stocks correctly.'],
  ['05', 'Score relative stress', 'Use historical percentiles and persistence signals—not unsupported absolute capacity claims.'],
  ['06', 'Write the evidence', 'Generate figures, tables, limitations, and an executive readout from processed outputs.'],
  ['07', 'Serve the surface', 'Expose load, flow balance, volatility, and data quality in a responsive Streamlit app.'],
];

const files = [
  ['data/', 'Immutable source and reproducible outputs'],
  ['notebooks/', 'Inspection, cleaning, EDA, and analysis narrative'],
  ['src/', 'Reusable cleaning, validation, metric, and visualization code'],
  ['dashboard/', 'Streamlit presentation layer'],
  ['reports/', 'Research paper, executive summary, figures, and tables'],
  ['tests/', 'Formula and data-quality safeguards'],
];

function SectionLabel({ children, dark = false }: { children: React.ReactNode; dark?: boolean }) {
  return (
    <div className={`section-label ${dark ? 'section-label-dark' : ''}`}>
      <span className="label-dot" />
      {children}
    </div>
  );
}

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [metricGroup, setMetricGroup] = useState<MetricGroup>('all');
  const [activeWorkflow, setActiveWorkflow] = useState(0);

  const visibleMetrics = metricGroup === 'all' ? metrics : metrics.filter((metric) => metric.group === metricGroup);

  const goTo = (id: string) => {
    setMenuOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <main>
      <header className="topbar">
        <button className="brand" onClick={() => goTo('top')} aria-label="Back to top">
          <span className="brand-mark"><Activity size={16} strokeWidth={2.4} /></span>
          <span>UAC / CARE LOAD</span>
        </button>
        <nav className={`nav-links ${menuOpen ? 'nav-links-open' : ''}`} aria-label="Primary navigation">
          <button onClick={() => goTo('architecture')}>Architecture</button>
          <button onClick={() => goTo('metrics')}>Metrics</button>
          <button onClick={() => goTo('workflow')}>Workflow</button>
          <button onClick={() => goTo('build-map')}>Build map</button>
        </nav>
        <div className="topbar-end">
          <span className="status-pill"><span className="status-pulse" /> Blueprint v1.0</span>
          <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </header>

      <section className="hero section-shell" id="top">
        <div className="hero-copy">
          <div className="eyebrow"><span>RESEARCH + IMPLEMENTATION BLUEPRINT</span><span className="eyebrow-line" /></div>
          <h1>Make the care pipeline <em>legible.</em></h1>
          <p className="hero-lede">A reproducible analytical system for turning UAC care-flow observations into a clearer view of load, pressure, and relief.</p>
          <div className="hero-actions">
            <button className="button-primary" onClick={() => goTo('architecture')}>Explore the system <ArrowRight size={17} /></button>
            <button className="button-quiet" onClick={() => goTo('metrics')}>View KPI definitions <MoveUpRight size={16} /></button>
          </div>
          <div className="hero-note"><ShieldCheck size={15} /> Designed to distinguish observed data, derived metrics, and analytical flags.</div>
        </div>
        <div className="hero-visual" aria-label="Care pipeline signal preview">
          <div className="visual-topline"><span>PIPELINE / SIGNAL MAP</span><span>01 — 07</span></div>
          <div className="signal-title">From intake to<br /><strong>reported relief.</strong></div>
          <div className="mini-chart">
            <svg viewBox="0 0 560 210" role="img" aria-label="Illustrative load trend lines">
              <defs>
                <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#f2a65a" stopOpacity=".3" /><stop offset="100%" stopColor="#f2a65a" stopOpacity="0" /></linearGradient>
              </defs>
              {[24, 70, 116, 162].map((y) => <line key={y} x1="0" x2="560" y1={y} y2={y} className="grid-line" />)}
              <path d="M0 166 C38 158 54 144 84 151 S135 145 166 126 S212 121 238 135 S275 115 309 106 S356 126 390 100 S442 78 468 88 S518 70 560 44 L560 210 L0 210Z" fill="url(#areaFill)" />
              <path d="M0 166 C38 158 54 144 84 151 S135 145 166 126 S212 121 238 135 S275 115 309 106 S356 126 390 100 S442 78 468 88 S518 70 560 44" className="chart-line chart-line-orange" />
              <path d="M0 180 C41 178 58 165 84 169 S139 156 169 160 S216 144 242 151 S285 132 316 138 S363 117 394 122 S440 108 473 109 S521 94 560 99" className="chart-line chart-line-blue" />
              <circle cx="560" cy="44" r="4" className="chart-point-orange" />
              <circle cx="560" cy="99" r="4" className="chart-point-blue" />
            </svg>
            <div className="chart-axis"><span>REPORTING OBSERVATIONS</span><span>LOAD →</span></div>
          </div>
          <div className="signal-legend"><span><i className="legend-orange" /> Total system load</span><span><i className="legend-blue" /> Relative flow balance</span></div>
          <div className="pipeline-row">
            <div><span className="pipeline-index">01</span><span>CBP intake</span></div><ArrowRight size={14} /><div><span className="pipeline-index">02</span><span>Transfer</span></div><ArrowRight size={14} /><div><span className="pipeline-index">03</span><span>HHS care</span></div><ArrowRight size={14} /><div><span className="pipeline-index">04</span><span>Discharge</span></div>
          </div>
        </div>
      </section>

      <div className="ticker"><div className="ticker-inner"><span className="ticker-kicker">THE ANALYTICAL SPINE</span><span>RAW SOURCE</span><ArrowRight size={14} /><span>VALIDATED TABLE</span><ArrowRight size={14} /><span>METRIC LAYER</span><ArrowRight size={14} /><span>EVIDENCE</span><ArrowRight size={14} /><span>DECISION SURFACE</span></div></div>

      <section className="section-shell intro-grid" id="architecture">
        <div className="intro-aside"><SectionLabel>01 / Why this exists</SectionLabel><p className="aside-caption">A system for seeing pressure before it becomes a story.</p></div>
        <div className="intro-content"><h2>Operational data is collected. <span>Operational clarity is built.</span></h2><p>The UAC program behaves like a dynamic care pipeline: children move through CBP custody, transfer into HHS care, receive medical and welfare support, and exit through sponsor placement. The analytical challenge is not a single chart. It is a shared language for load, flow, volatility, and uncertainty.</p><div className="callout"><div className="callout-icon"><Network size={20} /></div><div><strong>The core principle</strong><p>Keep the raw source immutable. Separate cleaning, validation, metric calculation, evidence, and presentation so every headline can be traced back to an observation and a formula.</p></div></div></div>
      </section>

      <section className="dark-section" id="metric-spine">
        <div className="section-shell dark-inner">
          <div className="dark-heading"><SectionLabel dark>02 / System architecture</SectionLabel><h2>Five layers.<br /><span>One source of truth.</span></h2><p>The dashboard is the final expression—not the place where business logic is invented.</p></div>
          <div className="layer-stack">
            {[
              ['01', 'Raw data', 'Immutable CSV + source metadata', Database],
              ['02', 'Preparation', 'Parse, standardize, flag', ShieldCheck],
              ['03', 'Analytical core', 'KPI and stress calculations', Gauge],
              ['04', 'Evidence', 'EDA, sensitivity, limitations', BarChart3],
              ['05', 'Presentation', 'Streamlit decision surface', PanelTop],
            ].map(([index, title, desc, Icon]) => <div className="layer-row" key={index as string}><span className="layer-number">{index as string}</span><Icon size={19} /><div className="layer-text"><strong>{title as string}</strong><span>{desc as string}</span></div><ArrowDownRight size={16} className="layer-arrow" /></div>)}
          </div>
        </div>
      </section>

      <section className="section-shell metrics-section" id="metrics">
        <div className="section-heading-row"><div><SectionLabel>03 / Metric layer</SectionLabel><h2>Make pressure <span>measurable.</span></h2></div><p>Transparent formulas turn operational signals into an analytical vocabulary. Each metric carries its own boundary conditions.</p></div>
        <div className="filter-row" role="group" aria-label="Filter metrics">
          {(['all', 'load', 'flow', 'diagnostic'] as MetricGroup[]).map((group) => <button key={group} className={metricGroup === group ? 'filter-active' : ''} onClick={() => setMetricGroup(group)}>{group === 'all' ? 'All metrics' : group === 'load' ? 'Load' : group === 'flow' ? 'Flow' : 'Diagnostics'}</button>)}
        </div>
        <div className="metric-grid">
          {visibleMetrics.map((metric) => <article className={`metric-card accent-${metric.accent}`} key={metric.name}><div className="metric-card-top"><span className="metric-tag">{metric.tag}</span><span className="metric-index">{String(metrics.indexOf(metric) + 1).padStart(2, '0')}</span></div><h3>{metric.name}</h3><div className="formula">{metric.formula}</div><p>{metric.description}</p><div className="metric-card-bottom"><span>{metric.group}</span><ArrowRight size={15} /></div></article>)}
        </div>
      </section>

      <section className="workflow-section" id="workflow">
        <div className="section-shell workflow-grid"><div className="workflow-sticky"><SectionLabel>04 / Workflow</SectionLabel><h2>From raw file<br />to <span>decision surface.</span></h2><p>Each stage has one job. The result is a pipeline that can be rerun, inspected, tested, and shared.</p><div className="workflow-progress"><div className="progress-track"><span style={{ width: `${((activeWorkflow + 1) / workflow.length) * 100}%` }} /></div><div><strong>{String(activeWorkflow + 1).padStart(2, '0')}</strong><span> / {String(workflow.length).padStart(2, '0')}</span></div></div></div><div className="workflow-list">{workflow.map(([num, title, desc], index) => <button className={`workflow-item ${activeWorkflow === index ? 'workflow-active' : ''}`} key={num} onClick={() => setActiveWorkflow(index)}><span className="workflow-num">{num}</span><div><h3>{title}</h3><p>{desc}</p></div><span className="workflow-check">{activeWorkflow > index ? <Check size={16} /> : <ArrowRight size={16} />}</span></button>)}</div></div>
      </section>

      <section className="section-shell build-section" id="build-map">
        <div className="section-heading-row"><div><SectionLabel>05 / Build map</SectionLabel><h2>Small enough to ship.<br /><span>Strong enough to trust.</span></h2></div><p>A minimal project structure keeps exploratory work visible without mixing it with the reusable analytical core.</p></div>
        <div className="build-grid"><div className="file-tree"><div className="tree-top"><FileCode2 size={17} /> UAC_Care_Load_Analytics/ <span>PROJECT ROOT</span></div>{files.map(([name, desc]) => <div className="tree-row" key={name}><span className="tree-branch">{name.endsWith('/') ? '├──' : '└──'}</span><strong>{name}</strong><span>{desc}</span></div>)}</div><div className="build-notes"><div className="note-card"><Sparkles size={18} /><div><strong>One command, many outputs</strong><p>The build process should create processed data, figures, report tables, and dashboard inputs from the raw source.</p></div></div><div className="note-card"><GitBranch size={18} /><div><strong>Notebooks explain. Modules repeat.</strong><p>Keep reusable transformations in <code>src/</code>. Use notebooks to show how findings were reached.</p></div></div><div className="note-card"><ShieldCheck size={18} /><div><strong>Test before you narrate</strong><p>Unit-test zero denominators, blank rows, missing dates, and flow-versus-stock review flags.</p></div></div></div></div>
      </section>

      <section className="limitations-section"><div className="section-shell limitations-grid"><div><SectionLabel>06 / Scientific boundary</SectionLabel><h2>Relative stress is not <span>absolute capacity.</span></h2></div><div className="limitation-content"><p className="large-copy">The dataset does not provide licensed beds, available beds, staffing levels, or facility operating limits. The first version can identify historical relative strain—but it cannot claim utilization, overcrowding, or a verified capacity breach.</p><div className="limitation-list"><div><CircleAlert size={17} /><span>Missing reporting dates mean “not observed,” not zero.</span></div><div><CircleAlert size={17} /><span>Same-day flows may not align with end-of-day stocks.</span></div><div><CircleAlert size={17} /><span>Aggregate observations support monitoring, not causal claims.</span></div></div></div></div></section>

      <section className="final-cta section-shell"><div className="cta-kicker"><span className="label-dot" /> READY FOR THE FIRST BUILD</div><h2>Turn the blueprint<br />into a <em>repeatable signal.</em></h2><button className="button-primary button-dark" onClick={() => goTo('top')}>Back to the beginning <ArrowRight size={17} /></button></section>

      <footer className="footer section-shell"><div className="footer-brand"><span className="brand-mark"><Activity size={16} /></span><span>UAC / CARE LOAD</span></div><p>System Capacity &amp; Care Load Analytics for Unaccompanied Children</p><span className="footer-meta">ARCHITECTURE BRIEF · 2026</span></footer>
    </main>
  );
}

export default App;
