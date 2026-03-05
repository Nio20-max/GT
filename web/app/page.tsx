export default function HomePage() {
  return (
    <main className="app-shell">
      <aside className="left-menu">
        <h1>Goal Tactics</h1>
        <nav>
          <a>Club</a>
          <a>Squad</a>
          <a>Lineup</a>
          <a>Training</a>
          <a>Market</a>
          <a>League</a>
        </nav>
      </aside>
      <section className="content">
        <header className="economy-bar">
          <span>Money: 5,000,000</span>
          <span>Stars: 20,000</span>
          <span>Medipacks: 0</span>
        </header>
        <article className="panel">
          <h2>Scaffold Ready</h2>
          <p>Web client scaffold is in place and aligned with GT dark-green visual direction.</p>
        </article>
      </section>
    </main>
  );
}
