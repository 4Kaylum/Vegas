CREATE TABLE IF NOT EXISTS guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);


CREATE TABLE IF NOT EXISTS user_settings(
    user_id BIGINT PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS role_list(
    guild_id BIGINT,
    role_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, role_id, key)
);


CREATE TABLE IF NOT EXISTS channel_list(
    guild_id BIGINT,
    channel_id BIGINT,
    key VARCHAR(50),
    value VARCHAR(50),
    PRIMARY KEY (guild_id, channel_id, key)
);


CREATE TABLE IF NOT EXISTS guild_currencies(
    guild_id BIGINT,
    currency_name TEXT,
    short_form TEXT,
    negative_amount_allowed BOOLEAN DEFAULT FALSE,
    allow_daily_command BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (guild_id, short_form),
    PRIMARY KEY (guild_id, currency_name)
);


-- CREATE TABLE IF NOT EXISTS user_money(
--     user_id BIGINT,
--     guild_id BIGINT,
--     currency_name TEXT,
--     money_amount BIGINT,
--     last_daily_command TIMESTAMP DEFAULT '2000-01-01',
--     PRIMARY KEY (user_id, guild_id, currency_name),
--     FOREIGN KEY (guild_id, currency_name) REFERENCES guild_currencies (guild_id, currency_name)
-- );


CREATE TABLE IF NOT EXISTS transactions(
    transaction_id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    currency_name TEXT,
    amount_transferred BIGINT,
    reason TEXT NOT NULL,
    win BOOLEAN
);
