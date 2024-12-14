CREATE TABLE transactions (
	date  VARCHAR(16),
	month VARCHAR(16),
	transaction VARCHAR(256),
	charges DECIMAL(10, 2),
	credits DECIMAL(10, 2)
);

select * from transactions;
--truncate table transactions;
--drop table transactions;