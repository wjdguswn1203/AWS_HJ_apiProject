CREATE TABLE `jpjoin`.`pyeup` (
  `id` VARCHAR(120) NOT NULL,
  `year` INT NOT NULL,
  `subject` VARCHAR(255) NOT NULL,
  `count` INT NOT NULL,
  `percentage` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`));

  CREATE TABLE `jpjoin`.`pyeupapi` (
  `id` VARCHAR(120) NOT NULL,
  `subject` VARCHAR(255) NOT NULL,
  `count` INT NOT NULL,
  PRIMARY KEY (`id`));
