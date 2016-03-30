CREATE TABLE `led_schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `length` int(11) NOT NULL,
  `code` text NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `position` int(10) unsigned DEFAULT NULL,
  `enabled` tinyint(4) DEFAULT '1',
  `time_from` time DEFAULT NULL,
  `time_to` time DEFAULT NULL,
  `days_of_week` varchar(7) DEFAULT NULL,
  `repeats` int(11) DEFAULT NULL,
  `date_from` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_led_schedule_1_idx` (`user_id`),
  CONSTRAINT `fk_led_schedule_1` FOREIGN KEY (`user_id`) REFERENCES `led_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;

CREATE TABLE `led_user` (
  `id` int(11) NOT NULL,
  `email` varchar(128) NOT NULL,
  `password` char(128) NOT NULL,
  `access_level` int(11) NOT NULL DEFAULT '0' COMMENT 'Access levels are: \n0: signed up, can view schedule\n1: can submit new code for scheduling\n2: can approve code and new users, as well as modifying the schedule',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
