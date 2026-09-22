import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

let poolConfig;

if (process.env.CLOUD_SQL_INSTANCE) {
  // Cloud Run: connect via Unix socket injected by Cloud SQL Proxy
  const socketPath = `/cloudsql/${process.env.CLOUD_SQL_INSTANCE}`;
  const url = new URL(process.env.DATABASE_URL);
  poolConfig = {
    user: decodeURIComponent(url.username),
    password: decodeURIComponent(url.password),
    database: url.pathname.slice(1),
    host: socketPath,
    ssl: false,
  };
} else {
  poolConfig = {
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_SSL === 'true' ? { rejectUnauthorized: false } : false,
    // The managed database scales to zero after a few minutes of inactivity and
    // drops open connections when it does. Retire idle clients before that
    // happens so the pool is not holding connections the server has closed.
    idleTimeoutMillis: 30000,
    // Fail a stalled connection attempt rather than hanging a request forever.
    connectionTimeoutMillis: 15000,
  };
}

// Shared connection pool so requests reuse database connections.
const pool = new Pool(poolConfig);

// An idle client losing its connection emits an error on the pool, not on the
// query that opened it. Without this listener Node treats it as an uncaught
// exception and `server.js` exits the process, so a routine database suspend
// takes the whole API down. Logging it lets the pool discard the dead client
// and open a fresh one on the next query.
pool.on('error', (err) => {
  console.error('Database pool error (idle client):', err.message);
});

export default pool;
