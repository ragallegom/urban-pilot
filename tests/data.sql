INSERT INTO user (first_name, middle_name, last_name, username, email, password, zip_code, city, state)
VALUES
  ('test', '', '1', 'test', 'test1@gmail.com', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', '00501', '', ''),
  ('test', '', '2', 'other', 'test2@gmail.com', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', '05030', '', '');

INSERT INTO post (title, body, author_id, created)
VALUES
  ('test title', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');