-- --------------------------------------------------------
-- 主机:                           127.0.0.1
-- 服务器版本:                        5.7.26 - MySQL Community Server (GPL)
-- 服务器操作系统:                      Win64
-- HeidiSQL 版本:                  11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
USE ecom_db;
-- 导出  表 ecom_db.admins 结构
CREATE TABLE IF NOT EXISTS `admins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'admin',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `permissions` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `ix_admins_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.admins 的数据：1 rows
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
TRUNCATE TABLE admins;
INSERT INTO `admins` (`id`, `email`, `password_hash`, `full_name`, `role`, `is_active`, `permissions`, `last_login_at`, `created_at`, `updated_at`) VALUES
	(1, 'admin@example.com', '$2b$12$9Dm6i3h4sdSR5zQ4vEDy1uNSEEJ3ije4RH8L36o6EdADmvSZeA98y', 'Super Admin', 'super_admin', 1, '{"seo": true, "tax": true, "admins": true, "orders": true, "banners": true, "content": true, "coupons": true, "reviews": true, "carriers": true, "channels": true, "payments": true, "products": true, "shipping": true, "inventory": true, "categories": true, "newsletter": true, "statistics": true, "email_templates": true}', '2026-03-23 06:12:34', '2026-03-17 07:59:00', '2026-03-23 14:12:34');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;

-- 导出  表 ecom_db.alembic_version 结构
CREATE TABLE IF NOT EXISTS `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.alembic_version 的数据：1 rows
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` (`version_num`) VALUES
	('002');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;

-- 导出  表 ecom_db.banners 结构
CREATE TABLE IF NOT EXISTS `banners` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subtitle` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `coupon_id` int(11) DEFAULT NULL,
  `link_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `starts_at` datetime DEFAULT NULL,
  `ends_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `sort_order` int(11) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `coupon_id` (`coupon_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.banners 的数据：0 rows
/*!40000 ALTER TABLE `banners` DISABLE KEYS */;
/*!40000 ALTER TABLE `banners` ENABLE KEYS */;

-- 导出  表 ecom_db.blog_categories 结构
CREATE TABLE IF NOT EXISTS `blog_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.blog_categories 的数据：0 rows
/*!40000 ALTER TABLE `blog_categories` DISABLE KEYS */;
/*!40000 ALTER TABLE `blog_categories` ENABLE KEYS */;

-- 导出  表 ecom_db.blog_posts 结构
CREATE TABLE IF NOT EXISTS `blog_posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `excerpt` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `author` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cover_image_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cover_storage_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'local',
  `category_id` int(11) DEFAULT NULL,
  `is_published` tinyint(1) NOT NULL DEFAULT '0',
  `published_at` datetime DEFAULT NULL,
  `seo_title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `seo_description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `og_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `category_id` (`category_id`),
  KEY `ix_blog_posts_is_published` (`is_published`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.blog_posts 的数据：0 rows
/*!40000 ALTER TABLE `blog_posts` DISABLE KEYS */;
/*!40000 ALTER TABLE `blog_posts` ENABLE KEYS */;

-- 导出  表 ecom_db.categories 结构
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `parent_id` int(11) DEFAULT NULL,
  `sort_order` smallint(6) NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_categories_slug` (`slug`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

TRUNCATE TABLE `categories`;
-- 正在导出表  ecom_db.categories 的数据：3 rows
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` (`id`, `name`, `slug`, `description`, `parent_id`, `sort_order`, `is_active`, `created_at`, `updated_at`) VALUES
	(1, '3C电子', '3c', '3c', NULL, 0, 1, '2026-03-23 14:48:10', '2026-03-23 14:48:10'),
	(2, '蓝牙耳机', 'bluetooth-a', 'aa', 1, 0, 1, '2026-03-23 14:48:33', '2026-03-23 14:48:33'),
	(3, '数据线', 'cable', 'cable', 1, 0, 1, '2026-03-23 14:51:20', '2026-03-23 14:51:20');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;

-- 导出  表 ecom_db.channel_events 结构
CREATE TABLE IF NOT EXISTS `channel_events` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `event_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `ix_channel_events_channel_id` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.channel_events 的数据：0 rows
/*!40000 ALTER TABLE `channel_events` DISABLE KEYS */;
/*!40000 ALTER TABLE `channel_events` ENABLE KEYS */;

-- 导出  表 ecom_db.cms_pages 结构
CREATE TABLE IF NOT EXISTS `cms_pages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `page_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `is_published` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_cms_pages_page_type` (`page_type`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
TRUNCATE TABLE `cms_pages`;
-- 正在导出表  ecom_db.cms_pages 的数据：14 rows
/*!40000 ALTER TABLE `cms_pages` DISABLE KEYS */;
INSERT INTO `cms_pages` (`id`, `page_type`, `language_code`, `title`, `content`, `is_published`, `created_at`, `updated_at`) VALUES
	(1, 'about_us', 'en', 'About Us', '<h1>About Us</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'about_us', 'es', 'Sobre Nosotros', '<h1>Sobre Nosotros</h1><p>Edita esta página en el panel admin.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'return_policy', 'en', 'Return Policy', '<h1>Return Policy</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'return_policy', 'es', 'Política de Devoluciones', '<h1>Política de Devoluciones</h1><p>Edita esta página.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'shipping_policy', 'en', 'Shipping Policy', '<h1>Shipping Policy</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(6, 'shipping_policy', 'es', 'Política de Envíos', '<h1>Política de Envíos</h1><p>Edita esta página.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(7, 'privacy_policy', 'en', 'Privacy Policy', '<h1>Privacy Policy</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(8, 'privacy_policy', 'es', 'Política de Privacidad', '<h1>Política de Privacidad</h1><p>Edita esta página.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(9, 'terms_of_service', 'en', 'Terms of Service', '<h1>Terms of Service</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(10, 'terms_of_service', 'es', 'Términos de Servicio', '<h1>Términos de Servicio</h1><p>Edita esta página.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(11, 'terms_of_use', 'en', 'Terms of Use', '<h1>Terms of Use</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(12, 'terms_of_use', 'es', 'Términos de Uso', '<h1>Términos de Uso</h1><p>Edita esta página.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(13, 'cookie_policy', 'en', 'Cookie Policy', '<h1>Cookie Policy</h1><p>Edit this page in the admin panel.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(14, 'cookie_policy', 'es', 'Política de Cookies', '<h1>Política de Cookies</h1><p>Edita esta página.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `cms_pages` ENABLE KEYS */;

-- 导出  表 ecom_db.cookie_consent_configs 结构
CREATE TABLE IF NOT EXISTS `cookie_consent_configs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `accept_btn` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reject_btn` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customize_btn` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.cookie_consent_configs 的数据：2 rows
/*!40000 ALTER TABLE `cookie_consent_configs` DISABLE KEYS */;
INSERT INTO `cookie_consent_configs` (`id`, `language_code`, `title`, `description`, `accept_btn`, `reject_btn`, `customize_btn`, `is_active`, `created_at`, `updated_at`) VALUES
	(1, 'en', 'We use cookies', 'We use cookies to improve your experience. By using our site, you agree to our cookie policy.', 'Accept All', 'Reject All', 'Customize', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'es', 'Usamos cookies', 'Usamos cookies para mejorar tu experiencia. Al usar nuestro sitio, aceptas nuestra política de cookies.', 'Aceptar Todo', 'Rechazar Todo', 'Personalizar', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `cookie_consent_configs` ENABLE KEYS */;

-- 导出  表 ecom_db.countries 结构
CREATE TABLE IF NOT EXISTS `countries` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `sort_order` smallint(6) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_countries_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
TRUNCATE TABLE `countries`;
-- 正在导出表  ecom_db.countries 的数据：10 rows
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
INSERT INTO `countries` (`id`, `name`, `code`, `is_active`, `sort_order`) VALUES
	(1, 'United States', 'US', 1, 1),
	(2, 'United Kingdom', 'GB', 1, 2),
	(3, 'Canada', 'CA', 1, 3),
	(4, 'Germany', 'DE', 1, 4),
	(5, 'France', 'FR', 1, 5),
	(6, 'Italy', 'IT', 1, 6),
	(7, 'Spain', 'ES', 1, 7),
	(8, 'Netherlands', 'NL', 1, 8),
	(9, 'Australia', 'AU', 1, 9),
	(10, 'Japan', 'JP', 1, 10);
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;

-- 导出  表 ecom_db.country_states 结构
CREATE TABLE IF NOT EXISTS `country_states` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `ix_country_states_country_code` (`country_code`)
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
TRUNCATE TABLE `country_states`;
-- 正在导出表  ecom_db.country_states 的数据：51 rows
/*!40000 ALTER TABLE `country_states` DISABLE KEYS */;
INSERT INTO `country_states` (`id`, `country_code`, `name`, `code`, `is_active`) VALUES
	(1, 'US', 'Alabama', 'AL', 1),
	(2, 'US', 'Alaska', 'AK', 0),
	(3, 'US', 'Arizona', 'AZ', 1),
	(4, 'US', 'Arkansas', 'AR', 1),
	(5, 'US', 'California', 'CA', 1),
	(6, 'US', 'Colorado', 'CO', 1),
	(7, 'US', 'Connecticut', 'CT', 1),
	(8, 'US', 'Delaware', 'DE', 1),
	(9, 'US', 'Florida', 'FL', 1),
	(10, 'US', 'Georgia', 'GA', 1),
	(11, 'US', 'Hawaii', 'HI', 0),
	(12, 'US', 'Idaho', 'ID', 1),
	(13, 'US', 'Illinois', 'IL', 1),
	(14, 'US', 'Indiana', 'IN', 1),
	(15, 'US', 'Iowa', 'IA', 1),
	(16, 'US', 'Kansas', 'KS', 1),
	(17, 'US', 'Kentucky', 'KY', 1),
	(18, 'US', 'Louisiana', 'LA', 1),
	(19, 'US', 'Maine', 'ME', 1),
	(20, 'US', 'Maryland', 'MD', 1),
	(21, 'US', 'Massachusetts', 'MA', 1),
	(22, 'US', 'Michigan', 'MI', 1),
	(23, 'US', 'Minnesota', 'MN', 1),
	(24, 'US', 'Mississippi', 'MS', 1),
	(25, 'US', 'Missouri', 'MO', 1),
	(26, 'US', 'Montana', 'MT', 1),
	(27, 'US', 'Nebraska', 'NE', 1),
	(28, 'US', 'Nevada', 'NV', 1),
	(29, 'US', 'New Hampshire', 'NH', 1),
	(30, 'US', 'New Jersey', 'NJ', 1),
	(31, 'US', 'New Mexico', 'NM', 1),
	(32, 'US', 'New York', 'NY', 1),
	(33, 'US', 'North Carolina', 'NC', 1),
	(34, 'US', 'North Dakota', 'ND', 1),
	(35, 'US', 'Ohio', 'OH', 1),
	(36, 'US', 'Oklahoma', 'OK', 1),
	(37, 'US', 'Oregon', 'OR', 1),
	(38, 'US', 'Pennsylvania', 'PA', 1),
	(39, 'US', 'Rhode Island', 'RI', 1),
	(40, 'US', 'South Carolina', 'SC', 1),
	(41, 'US', 'South Dakota', 'SD', 1),
	(42, 'US', 'Tennessee', 'TN', 1),
	(43, 'US', 'Texas', 'TX', 1),
	(44, 'US', 'Utah', 'UT', 1),
	(45, 'US', 'Vermont', 'VT', 1),
	(46, 'US', 'Virginia', 'VA', 1),
	(47, 'US', 'Washington', 'WA', 1),
	(48, 'US', 'West Virginia', 'WV', 1),
	(49, 'US', 'Wisconsin', 'WI', 1),
	(50, 'US', 'Wyoming', 'WY', 1),
	(51, 'US', 'Washington D.C.', 'DC', 1);
/*!40000 ALTER TABLE `country_states` ENABLE KEYS */;

-- 导出  表 ecom_db.coupons 结构
CREATE TABLE IF NOT EXISTS `coupons` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` decimal(10,2) NOT NULL DEFAULT '0.00',
  `min_order_amount` decimal(10,2) DEFAULT NULL,
  `max_uses` int(11) DEFAULT NULL,
  `used_count` int(11) NOT NULL DEFAULT '0',
  `starts_at` datetime DEFAULT NULL,
  `ends_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `ix_coupons_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.coupons 的数据：1 rows
/*!40000 ALTER TABLE `coupons` DISABLE KEYS */;
INSERT INTO `coupons` (`id`, `code`, `type`, `value`, `min_order_amount`, `max_uses`, `used_count`, `starts_at`, `ends_at`, `is_active`, `description`, `created_at`, `updated_at`) VALUES
	(1, 'BLK520', 'fixed', 10.00, 20.00, 100, 0, '2026-03-23 06:13:46', '2026-04-30 06:13:49', 1, NULL, '2026-03-23 14:13:52', '2026-03-23 14:13:52');
/*!40000 ALTER TABLE `coupons` ENABLE KEYS */;

-- 导出  表 ecom_db.email_templates 结构
CREATE TABLE IF NOT EXISTS `email_templates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `subject` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `body` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_email_templates_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.email_templates 的数据：12 rows
/*!40000 ALTER TABLE `email_templates` DISABLE KEYS */;
INSERT INTO `email_templates` (`id`, `type`, `language_code`, `subject`, `body`, `is_active`, `created_at`, `updated_at`) VALUES
	(1, 'order_confirmation', 'en', 'Order Confirmed — #{{order_id}}', '<h2>Thank you, {{customer_name}}!</h2><p>Your order <strong>#{{order_id}}</strong> has been confirmed.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'order_confirmation', 'es', 'Pedido Confirmado — #{{order_id}}', '<h2>¡Gracias, {{customer_name}}!</h2><p>Tu pedido <strong>#{{order_id}}</strong> ha sido confirmado.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'order_shipped', 'en', 'Your order has shipped! 🚚', '<h2>Great news, {{customer_name}}!</h2><p>Order #{{order_id}} is on its way via {{carrier_name}}.</p><p>Tracking: <a href=\'{{tracking_url}}\'>{{tracking_no}}</a></p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'order_shipped', 'es', '¡Tu pedido está en camino! 🚚', '<h2>¡Buenas noticias, {{customer_name}}!</h2><p>El pedido #{{order_id}} está en camino con {{carrier_name}}.</p><p>Rastreo: <a href=\'{{tracking_url}}\'>{{tracking_no}}</a></p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'order_cancelled', 'en', 'Your order #{{order_id}} has been cancelled', '<p>Hi {{customer_name}}, your order #{{order_id}} has been cancelled.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(6, 'order_cancelled', 'es', 'Tu pedido #{{order_id}} ha sido cancelado', '<p>Hola {{customer_name}}, tu pedido #{{order_id}} ha sido cancelado.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(7, 'order_refunded', 'en', 'Refund processed for order #{{order_id}}', '<p>Hi {{customer_name}}, a refund of ${{refund_amount}} has been processed for order #{{order_id}}.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(8, 'order_refunded', 'es', 'Reembolso procesado para el pedido #{{order_id}}', '<p>Hola {{customer_name}}, se procesó un reembolso de ${{refund_amount}} para el pedido #{{order_id}}.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(9, 'payment_failed', 'en', 'Action required: Complete your order #{{order_id}}', '<p>Hi {{customer_name}}, your payment for order #{{order_id}} failed. Reason: {{fail_reason}}.</p><p><a href=\'{{retry_url}}\'>Click here to retry payment</a></p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(10, 'payment_failed', 'es', 'Acción requerida: Completa tu pedido #{{order_id}}', '<p>Hola {{customer_name}}, el pago del pedido #{{order_id}} falló. Motivo: {{fail_reason}}.</p><p><a href=\'{{retry_url}}\'>Haz clic aquí para reintentar el pago</a></p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(11, 'password_reset', 'en', 'Reset your password', '<p>Hi {{customer_name}}, click the link below to reset your password:</p><p><a href=\'{{reset_url}}\'>Reset Password</a></p><p>This link expires in 1 hour.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(12, 'password_reset', 'es', 'Restablece tu contraseña', '<p>Hola {{customer_name}}, haz clic en el enlace para restablecer tu contraseña:</p><p><a href=\'{{reset_url}}\'>Restablecer Contraseña</a></p><p>Este enlace expira en 1 hora.</p>', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `email_templates` ENABLE KEYS */;

-- 导出  表 ecom_db.faqs 结构
CREATE TABLE IF NOT EXISTS `faqs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `answer` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` smallint(6) NOT NULL DEFAULT '0',
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.faqs 的数据：0 rows
/*!40000 ALTER TABLE `faqs` DISABLE KEYS */;
/*!40000 ALTER TABLE `faqs` ENABLE KEYS */;

-- 导出  表 ecom_db.guest_claim_tokens 结构
CREATE TABLE IF NOT EXISTS `guest_claim_tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `token` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.guest_claim_tokens 的数据：0 rows
/*!40000 ALTER TABLE `guest_claim_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `guest_claim_tokens` ENABLE KEYS */;

-- 导出  表 ecom_db.inventory_logs 结构
CREATE TABLE IF NOT EXISTS `inventory_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sku_id` int(11) NOT NULL,
  `change_qty` int(11) NOT NULL,
  `before_qty` int(11) NOT NULL,
  `after_qty` int(11) NOT NULL,
  `reason` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reference_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `operator_id` (`operator_id`),
  KEY `ix_inventory_logs_sku_id` (`sku_id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.inventory_logs 的数据：7 rows
/*!40000 ALTER TABLE `inventory_logs` DISABLE KEYS */;
INSERT INTO `inventory_logs` (`id`, `sku_id`, `change_qty`, `before_qty`, `after_qty`, `reason`, `reference_id`, `operator_id`, `created_at`) VALUES
	(1, 8, -2, 111, 109, 'order', '1', NULL, '2026-03-23 19:38:41'),
	(2, 3, -1, 111, 110, 'order', '2', NULL, '2026-03-24 09:40:55'),
	(3, 3, -2, 110, 108, 'order', '3', NULL, '2026-03-24 09:53:12'),
	(4, 3, -2, 108, 106, 'order', '4', NULL, '2026-03-24 09:57:13'),
	(5, 3, -2, 106, 104, 'order', '5', NULL, '2026-03-24 10:04:14'),
	(6, 3, -4, 104, 100, 'order', '6', NULL, '2026-03-24 10:06:07'),
	(7, 3, -4, 100, 96, 'order', '7', NULL, '2026-03-24 10:11:39'),
	(8, 3, -2, 96, 94, 'order', '8', NULL, '2026-03-24 11:10:07'),
	(9, 3, -1, 94, 93, 'order', '9', NULL, '2026-03-24 11:43:57'),
	(10, 3, -1, 93, 92, 'order', '10', NULL, '2026-03-24 13:52:31'),
	(11, 3, 1, 92, 93, 'order_cancelled', '10', NULL, '2026-03-24 14:19:38'),
	(12, 4, -1, 111, 110, 'order', '11', NULL, '2026-03-24 14:21:02'),
	(13, 4, -1, 110, 109, 'order', '12', NULL, '2026-03-24 14:23:48'),
	(14, 5, -7, 111, 104, 'order', '13', NULL, '2026-03-24 14:24:29'),
	(15, 9, -6, 111, 105, 'order', '14', NULL, '2026-03-24 15:54:23'),
	(16, 14, -2, 111, 109, 'order', '15', NULL, '2026-03-24 15:56:24'),
	(17, 3, -4, 93, 89, 'order', '16', NULL, '2026-03-24 16:03:00'),
	(18, 3, -2, 89, 87, 'order', '17', NULL, '2026-03-24 16:04:06'),
	(19, 3, -2, 87, 85, 'order', '18', NULL, '2026-03-24 17:25:04'),
	(20, 3, -5, 85, 80, 'order', '19', NULL, '2026-03-24 17:26:04'),
	(21, 8, -5, 109, 104, 'order', '20', NULL, '2026-03-24 17:28:27'),
	(22, 5, -1, 104, 103, 'order', '21', NULL, '2026-03-24 17:37:42'),
	(23, 6, -1, 111, 110, 'order', '21', NULL, '2026-03-24 17:37:42'),
	(24, 3, -1, 80, 79, 'order', '21', NULL, '2026-03-24 17:37:42'),
	(25, 3, -1, 79, 78, 'order', '22', NULL, '2026-03-24 17:42:50'),
	(26, 3, -1, 78, 77, 'order', '23', NULL, '2026-03-24 17:43:32'),
	(27, 3, -1, 77, 76, 'order', '24', NULL, '2026-03-24 18:08:56'),
	(28, 3, -7, 76, 69, 'order', '25', NULL, '2026-03-24 18:15:22');
/*!40000 ALTER TABLE `inventory_logs` ENABLE KEYS */;

-- 导出  表 ecom_db.language_packs 结构
CREATE TABLE IF NOT EXISTS `language_packs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pack_key` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pack_value` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_language_packs_lang` (`language_code`)
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.language_packs 的数据：70 rows
/*!40000 ALTER TABLE `language_packs` DISABLE KEYS */;
INSERT INTO `language_packs` (`id`, `language_code`, `pack_key`, `pack_value`, `created_at`, `updated_at`) VALUES
	(1, 'en', 'nav.products', 'Products', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'en', 'nav.blog', 'Blog', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'en', 'nav.faq', 'FAQ', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'en', 'nav.about', 'About Us', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'en', 'nav.contact', 'Contact', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(6, 'en', 'cart.title', 'Shopping Cart', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(7, 'en', 'cart.empty', 'Your cart is empty', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(8, 'en', 'cart.add', 'Add to Cart', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(9, 'en', 'cart.checkout', 'Checkout', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(10, 'en', 'checkout.place_order', 'Place Order', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(11, 'en', 'checkout.shipping', 'Shipping', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(12, 'en', 'checkout.payment', 'Payment', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(13, 'en', 'checkout.summary', 'Order Summary', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(14, 'en', 'checkout.free_shipping', 'Free shipping on orders over ${{threshold}}', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(15, 'en', 'checkout.spend_more', 'Spend ${{amount}} more for free shipping', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(16, 'en', 'auth.sign_in', 'Sign In', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(17, 'en', 'auth.sign_up', 'Create Account', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(18, 'en', 'auth.sign_out', 'Sign Out', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(19, 'en', 'auth.email', 'Email Address', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(20, 'en', 'auth.password', 'Password', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(21, 'en', 'auth.forgot_password', 'Forgot password?', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(22, 'en', 'auth.agree_terms', 'I agree to the Terms of Service and Privacy Policy', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(23, 'en', 'product.reviews', 'Reviews', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(24, 'en', 'product.add_to_wishlist', 'Save', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(25, 'en', 'product.in_stock', 'In Stock', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(26, 'en', 'product.out_of_stock', 'Out of Stock', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(27, 'en', 'order.status.pending_payment', 'Pending Payment', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(28, 'en', 'order.status.pending_shipment', 'Processing', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(29, 'en', 'order.status.shipped', 'Shipped', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(30, 'en', 'order.status.completed', 'Completed', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(31, 'en', 'order.status.cancelled', 'Cancelled', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(32, 'en', 'order.status.refunded', 'Refunded', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(33, 'en', 'footer.newsletter_title', 'Stay in the loop', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(34, 'en', 'footer.newsletter_placeholder', 'Your email address', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(35, 'en', 'footer.newsletter_btn', 'Subscribe', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(36, 'es', 'nav.products', 'Productos', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(37, 'es', 'nav.blog', 'Blog', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(38, 'es', 'nav.faq', 'Preguntas Frecuentes', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(39, 'es', 'nav.about', 'Sobre Nosotros', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(40, 'es', 'nav.contact', 'Contacto', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(41, 'es', 'cart.title', 'Carrito de Compras', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(42, 'es', 'cart.empty', 'Tu carrito está vacío', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(43, 'es', 'cart.add', 'Agregar al Carrito', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(44, 'es', 'cart.checkout', 'Pagar', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(45, 'es', 'checkout.place_order', 'Realizar Pedido', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(46, 'es', 'checkout.shipping', 'Envío', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(47, 'es', 'checkout.payment', 'Pago', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(48, 'es', 'checkout.summary', 'Resumen del Pedido', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(49, 'es', 'checkout.free_shipping', 'Envío gratis en pedidos mayores a ${{threshold}}', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(50, 'es', 'checkout.spend_more', 'Gasta ${{amount}} más para envío gratis', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(51, 'es', 'auth.sign_in', 'Iniciar Sesión', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(52, 'es', 'auth.sign_up', 'Crear Cuenta', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(53, 'es', 'auth.sign_out', 'Cerrar Sesión', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(54, 'es', 'auth.email', 'Correo Electrónico', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(55, 'es', 'auth.password', 'Contraseña', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(56, 'es', 'auth.forgot_password', '¿Olvidaste tu contraseña?', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(57, 'es', 'auth.agree_terms', 'Acepto los Términos de Servicio y la Política de Privacidad', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(58, 'es', 'product.reviews', 'Reseñas', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(59, 'es', 'product.add_to_wishlist', 'Guardar', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(60, 'es', 'product.in_stock', 'En Stock', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(61, 'es', 'product.out_of_stock', 'Sin Stock', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(62, 'es', 'order.status.pending_payment', 'Pago Pendiente', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(63, 'es', 'order.status.pending_shipment', 'Procesando', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(64, 'es', 'order.status.shipped', 'Enviado', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(65, 'es', 'order.status.completed', 'Completado', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(66, 'es', 'order.status.cancelled', 'Cancelado', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(67, 'es', 'order.status.refunded', 'Reembolsado', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(68, 'es', 'footer.newsletter_title', 'Mantente informado', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(69, 'es', 'footer.newsletter_placeholder', 'Tu correo electrónico', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(70, 'es', 'footer.newsletter_btn', 'Suscribirse', '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `language_packs` ENABLE KEYS */;

-- 导出  表 ecom_db.logistics_carriers 结构
CREATE TABLE IF NOT EXISTS `logistics_carriers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tracking_url_template` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `applicable_countries` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.logistics_carriers 的数据：5 rows
/*!40000 ALTER TABLE `logistics_carriers` DISABLE KEYS */;
INSERT INTO `logistics_carriers` (`id`, `name`, `code`, `tracking_url_template`, `applicable_countries`, `is_active`, `created_at`, `updated_at`) VALUES
	(1, 'UPS', 'ups', 'https://www.ups.com/track?tracknum={tracking_no}', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'FedEx', 'fedex', 'https://www.fedex.com/fedextrack/?tracknumbers={tracking_no}', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'USPS', 'usps', 'https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_no}', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'DHL', 'dhl', 'https://www.dhl.com/en/express/tracking.html?AWB={tracking_no}', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'Royal Mail', 'royal_mail', 'https://www.royalmail.com/track-your-item#/tracking-results/{tracking_no}', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `logistics_carriers` ENABLE KEYS */;

-- 导出  表 ecom_db.marketing_channels 结构
CREATE TABLE IF NOT EXISTS `marketing_channels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ref_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `platform` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ref_code` (`ref_code`),
  KEY `ix_marketing_channels_ref_code` (`ref_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.marketing_channels 的数据：0 rows
/*!40000 ALTER TABLE `marketing_channels` DISABLE KEYS */;
/*!40000 ALTER TABLE `marketing_channels` ENABLE KEYS */;

-- 导出  表 ecom_db.media_files 结构
CREATE TABLE IF NOT EXISTS `media_files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `path` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `storage_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mime_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `size_bytes` int(11) DEFAULT NULL,
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `uploaded_by` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `uploaded_by` (`uploaded_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.media_files 的数据：0 rows
/*!40000 ALTER TABLE `media_files` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_files` ENABLE KEYS */;

-- 导出  表 ecom_db.newsletter_subscribers 结构
CREATE TABLE IF NOT EXISTS `newsletter_subscribers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `source` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'footer',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `unsub_token` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subscribed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `unsubscribed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `unsub_token` (`unsub_token`),
  KEY `ix_newsletter_subscribers_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.newsletter_subscribers 的数据：0 rows
/*!40000 ALTER TABLE `newsletter_subscribers` DISABLE KEYS */;
/*!40000 ALTER TABLE `newsletter_subscribers` ENABLE KEYS */;

-- 导出  表 ecom_db.oauth_accounts 结构
CREATE TABLE IF NOT EXISTS `oauth_accounts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `provider` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `provider_user_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `access_token` text COLLATE utf8mb4_unicode_ci,
  `refresh_token` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.oauth_accounts 的数据：0 rows
/*!40000 ALTER TABLE `oauth_accounts` DISABLE KEYS */;
/*!40000 ALTER TABLE `oauth_accounts` ENABLE KEYS */;

-- 导出  表 ecom_db.orders 结构
CREATE TABLE IF NOT EXISTS `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_no` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending_payment',
  `subtotal` decimal(10,2) NOT NULL,
  `shipping_fee` decimal(10,2) NOT NULL DEFAULT '0.00',
  `tax_amount` decimal(10,2) NOT NULL DEFAULT '0.00',
  `discount_amount` decimal(10,2) NOT NULL DEFAULT '0.00',
  `total_amount` decimal(10,2) NOT NULL,
  `payment_method` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unpaid',
  `coupon_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_address` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_zone_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `shipping_rule_id` int(11) DEFAULT NULL,
  `tax_rule_id` int(11) DEFAULT NULL,
  `tax_rate_snapshot` decimal(5,4) DEFAULT NULL,
  `channel_ref` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `channel_id` int(11) DEFAULT NULL,
  `guest_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `customer_note` text COLLATE utf8mb4_unicode_ci,
  `admin_note` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_no` (`order_no`),
  KEY `shipping_rule_id` (`shipping_rule_id`),
  KEY `tax_rule_id` (`tax_rule_id`),
  KEY `channel_id` (`channel_id`),
  KEY `ix_orders_order_no` (`order_no`),
  KEY `ix_orders_user_id` (`user_id`),
  KEY `ix_orders_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.orders 的数据：7 rows
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` (`id`, `order_no`, `user_id`, `status`, `subtotal`, `shipping_fee`, `tax_amount`, `discount_amount`, `total_amount`, `payment_method`, `payment_status`, `coupon_code`, `shipping_address`, `shipping_zone_name`, `shipping_rule_id`, `tax_rule_id`, `tax_rate_snapshot`, `channel_ref`, `channel_id`, `guest_email`, `language_code`, `customer_note`, `admin_note`, `created_at`, `updated_at`) VALUES
	(1, 'ORD-20260323-60C4319C', NULL, 'pending_payment', 44.00, 5.99, 0.00, 0.00, 49.99, 'airwallex', 'unpaid', NULL, '{"city": "los angeles", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "PA", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, 'Morrie green', 'en', NULL, NULL, '2026-03-23 19:38:41', '2026-03-23 19:38:41'),
	(2, 'ORD-20260324-BC0B2648', 1, 'cancelled', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 09:40:55', '2026-03-24 14:20:00'),
	(3, 'ORD-20260324-CD838D79', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AR", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 09:53:12', '2026-03-24 09:53:12'),
	(4, 'ORD-20260324-2B8CAB0F', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AZ", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 09:57:13', '2026-03-24 09:57:13'),
	(5, 'ORD-20260324-FD74CF9F', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 10:04:14', '2026-03-24 10:04:14'),
	(6, 'ORD-20260324-FC3E4F3B', 1, 'pending_payment', 88.00, 0.00, 0.00, 0.00, 88.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 10:06:07', '2026-03-24 10:06:07'),
	(7, 'ORD-20260324-23C6C7B8', 1, 'pending_payment', 88.00, 0.00, 0.00, 0.00, 88.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 10:11:39', '2026-03-24 10:11:39'),
	(8, 'ORD-20260324-4B0AE131', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 11:10:07', '2026-03-24 11:10:07'),
	(9, 'ORD-20260324-DF9C30BA', 1, 'pending_payment', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 11:43:57', '2026-03-24 11:43:57'),
	(10, 'ORD-20260324-82454E08', 1, 'cancelled', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 13:52:31', '2026-03-24 14:19:38'),
	(11, 'ORD-20260324-C79D892E', 1, 'pending_payment', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 14:21:02', '2026-03-24 14:21:02'),
	(12, 'ORD-20260324-FCC7D62B', 1, 'pending_payment', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 14:23:48', '2026-03-24 14:23:48'),
	(13, 'ORD-20260324-3E4D9C62', 1, 'pending_payment', 154.00, 0.00, 0.00, 0.00, 154.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 14:24:29', '2026-03-24 14:24:29'),
	(14, 'ORD-20260324-ABFB4B51', 1, 'pending_payment', 132.00, 0.00, 0.00, 0.00, 132.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 15:54:23', '2026-03-24 15:54:23'),
	(15, 'ORD-20260324-FA0EA6AA', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'stripe', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 15:56:24', '2026-03-24 15:56:24'),
	(16, 'ORD-20260324-5F0649B6', 1, 'pending_payment', 88.00, 0.00, 0.00, 0.00, 88.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 16:03:00', '2026-03-24 16:03:00'),
	(17, 'ORD-20260324-C400C3BF', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 16:04:06', '2026-03-24 16:04:06'),
	(18, 'ORD-20260324-AA17549B', 1, 'pending_payment', 44.00, 0.00, 0.00, 0.00, 44.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 17:25:04', '2026-03-24 17:25:04'),
	(19, 'ORD-20260324-CF455FDE', 1, 'pending_payment', 110.00, 0.00, 0.00, 0.00, 110.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 17:26:04', '2026-03-24 17:26:04'),
	(20, 'ORD-20260324-33EC4A0C', 1, 'pending_payment', 110.00, 0.00, 0.00, 0.00, 110.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 17:28:27', '2026-03-24 17:28:27'),
	(21, 'ORD-20260324-416E3C3D', 1, 'pending_payment', 66.00, 0.00, 0.00, 0.00, 66.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 17:37:42', '2026-03-24 17:37:42'),
	(22, 'ORD-20260324-4E0F2159', 1, 'pending_payment', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 17:42:50', '2026-03-24 17:42:50'),
	(23, 'ORD-20260324-3B35ED64', 1, 'pending_payment', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 17:43:32', '2026-03-24 17:43:32'),
	(24, 'ORD-20260324-0D728A43', 1, 'pending_payment', 22.00, 0.00, 0.00, 0.00, 22.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 18:08:56', '2026-03-24 18:08:56'),
	(25, 'ORD-20260324-E48D625A', 1, 'pending_payment', 154.00, 0.00, 0.00, 0.00, 154.00, 'airwallex', 'unpaid', NULL, '{"city": "Shenzhen", "phone": "+8616675345612", "full_name": "Morrie green", "state_code": "AL", "state_name": "", "postal_code": "512000", "country_code": "US", "address_line1": "Longgang", "address_line2": "Bantian"}', 'US Mainland', 1, NULL, 0.0000, NULL, NULL, NULL, 'en', NULL, NULL, '2026-03-24 18:15:22', '2026-03-24 18:15:22');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;

-- 导出  表 ecom_db.order_items 结构
CREATE TABLE IF NOT EXISTS `order_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `sku_id` int(11) DEFAULT NULL,
  `product_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sku_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `variant_attrs` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `product_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sku_id` (`sku_id`),
  KEY `ix_order_items_order_id` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.order_items 的数据：2 rows
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` (`id`, `order_id`, `sku_id`, `product_name`, `sku_code`, `variant_attrs`, `quantity`, `unit_price`, `subtotal`, `product_image`) VALUES
	(1, 6, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 4, 22.00, 88.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(2, 7, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 4, 22.00, 88.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(3, 8, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 2, 22.00, 44.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(4, 9, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(5, 10, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(6, 11, 4, '2222222', 'RED-XXL', '{"SIze": "XXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(7, 12, 4, '2222222', 'RED-XXL', '{"SIze": "XXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(8, 13, 5, '2222222', 'RED-XL', '{"SIze": "XL", "Color": "red"}', 7, 22.00, 154.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(9, 14, 9, '2222222', 'GREEN-XL', '{"SIze": "XL", "Color": "green"}', 6, 22.00, 132.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(10, 15, 14, '2222222', 'BLACH-L', '{"SIze": "L", "Color": "blach"}', 2, 22.00, 44.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(11, 16, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 4, 22.00, 88.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(12, 17, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 2, 22.00, 44.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(13, 18, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 2, 22.00, 44.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(14, 19, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 5, 22.00, 110.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(15, 20, 8, '2222222', 'GREEN-XXL', '{"SIze": "XXL", "Color": "green"}', 5, 22.00, 110.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(16, 21, 5, '2222222', 'RED-XL', '{"SIze": "XL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(17, 21, 6, '2222222', 'RED-L', '{"SIze": "L", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(18, 21, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(19, 22, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(20, 23, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(21, 24, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 1, 22.00, 22.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg'),
	(22, 25, 3, '2222222', 'RED-XXXL', '{"SIze": "XXXL", "Color": "red"}', 7, 22.00, 154.00, 'http://localhost:8000/media/products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;

-- 导出  表 ecom_db.order_status_logs 结构
CREATE TABLE IF NOT EXISTS `order_status_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `from_status` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `to_status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `note` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operator_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `operator_id` (`operator_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.order_status_logs 的数据：2 rows
/*!40000 ALTER TABLE `order_status_logs` DISABLE KEYS */;
INSERT INTO `order_status_logs` (`id`, `order_id`, `from_status`, `to_status`, `note`, `operator_id`, `created_at`) VALUES
	(1, 6, NULL, 'pending_payment', NULL, NULL, '2026-03-24 10:06:07'),
	(2, 7, NULL, 'pending_payment', NULL, NULL, '2026-03-24 10:11:39'),
	(3, 8, NULL, 'pending_payment', NULL, NULL, '2026-03-24 11:10:08'),
	(4, 9, NULL, 'pending_payment', NULL, NULL, '2026-03-24 11:43:58'),
	(5, 10, NULL, 'pending_payment', NULL, NULL, '2026-03-24 13:52:32'),
	(6, 10, 'pending_payment', 'cancelled', 'Cancelled by customer', NULL, '2026-03-24 14:19:38'),
	(7, 2, 'pending_payment', 'cancelled', 'Cancelled by customer', NULL, '2026-03-24 14:20:00'),
	(8, 11, NULL, 'pending_payment', NULL, NULL, '2026-03-24 14:21:02'),
	(9, 12, NULL, 'pending_payment', NULL, NULL, '2026-03-24 14:23:48'),
	(10, 13, NULL, 'pending_payment', NULL, NULL, '2026-03-24 14:24:30'),
	(11, 14, NULL, 'pending_payment', NULL, NULL, '2026-03-24 15:54:23'),
	(12, 15, NULL, 'pending_payment', NULL, NULL, '2026-03-24 15:56:24'),
	(13, 16, NULL, 'pending_payment', NULL, NULL, '2026-03-24 16:03:00'),
	(14, 17, NULL, 'pending_payment', NULL, NULL, '2026-03-24 16:04:06'),
	(15, 18, NULL, 'pending_payment', NULL, NULL, '2026-03-24 17:25:04'),
	(16, 19, NULL, 'pending_payment', NULL, NULL, '2026-03-24 17:26:04'),
	(17, 20, NULL, 'pending_payment', NULL, NULL, '2026-03-24 17:28:27'),
	(18, 21, NULL, 'pending_payment', NULL, NULL, '2026-03-24 17:37:42'),
	(19, 22, NULL, 'pending_payment', NULL, NULL, '2026-03-24 17:42:50'),
	(20, 23, NULL, 'pending_payment', NULL, NULL, '2026-03-24 17:43:32'),
	(21, 24, NULL, 'pending_payment', NULL, NULL, '2026-03-24 18:08:56'),
	(22, 25, NULL, 'pending_payment', NULL, NULL, '2026-03-24 18:15:22');
/*!40000 ALTER TABLE `order_status_logs` ENABLE KEYS */;

-- 导出  表 ecom_db.password_reset_tokens 结构
CREATE TABLE IF NOT EXISTS `password_reset_tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `token` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token` (`token`),
  KEY `user_id` (`user_id`),
  KEY `ix_password_reset_tokens_token` (`token`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.password_reset_tokens 的数据：0 rows
/*!40000 ALTER TABLE `password_reset_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `password_reset_tokens` ENABLE KEYS */;

-- 导出  表 ecom_db.payments 结构
CREATE TABLE IF NOT EXISTS `payments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `provider` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `provider_payment_id` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `currency` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'USD',
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `raw_response` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_payments_order_id` (`order_id`),
  KEY `ix_payments_provider_payment_id` (`provider_payment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.payments 的数据：0 rows
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;

-- 导出  表 ecom_db.payment_failed_email_logs 结构
CREATE TABLE IF NOT EXISTS `payment_failed_email_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.payment_failed_email_logs 的数据：0 rows
/*!40000 ALTER TABLE `payment_failed_email_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_failed_email_logs` ENABLE KEYS */;

-- 导出  表 ecom_db.payment_webhooks 结构
CREATE TABLE IF NOT EXISTS `payment_webhooks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `provider` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `event_id` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `order_id` int(11) DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'received',
  `raw_payload` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `error_msg` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `processed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `event_id` (`event_id`),
  KEY `ix_payment_webhooks_provider` (`provider`),
  KEY `ix_payment_webhooks_event_type` (`event_type`),
  KEY `ix_payment_webhooks_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.payment_webhooks 的数据：0 rows
/*!40000 ALTER TABLE `payment_webhooks` DISABLE KEYS */;
/*!40000 ALTER TABLE `payment_webhooks` ENABLE KEYS */;

-- 导出  表 ecom_db.products 结构
CREATE TABLE IF NOT EXISTS `products` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `short_desc` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `is_published` tinyint(1) NOT NULL DEFAULT '0',
  `rating_avg` float NOT NULL DEFAULT '0',
  `rating_count` int(11) NOT NULL DEFAULT '0',
  `seo_title` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `seo_description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `seo_slug` varchar(280) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `og_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `category_id` (`category_id`),
  KEY `ix_products_slug` (`slug`),
  KEY `ix_products_is_published` (`is_published`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.products 的数据：2 rows
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` (`id`, `name`, `slug`, `description`, `short_desc`, `category_id`, `is_published`, `rating_avg`, `rating_count`, `seo_title`, `seo_description`, `seo_slug`, `og_image`, `created_at`, `updated_at`) VALUES
	(1, '11111111111111', 'ff', 'ffffffffff', 'gggg', 3, 1, 0, 0, 'ffffffff', 'gggggggggg', NULL, NULL, '2026-03-23 14:59:05', '2026-03-23 15:23:46'),
	(2, '2222222', '2222222', '222222222222222222222222', 'fffffffffff', 2, 1, 0, 0, '', '', NULL, NULL, '2026-03-23 15:23:10', '2026-03-23 15:23:36');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;

-- 导出  表 ecom_db.product_images 结构
CREATE TABLE IF NOT EXISTS `product_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `storage_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'local',
  `alt_text` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sort_order` smallint(6) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.product_images 的数据：3 rows
/*!40000 ALTER TABLE `product_images` DISABLE KEYS */;
INSERT INTO `product_images` (`id`, `product_id`, `url`, `storage_type`, `alt_text`, `sort_order`, `created_at`) VALUES
	(1, 1, 'products/1/c202722a5d714aa7bf86d45bc9f84c67.png', 'local', '53A', 1, '2026-03-23 15:09:22'),
	(2, 2, 'products/2/6ae58aba5035468eb8fcaad29a92d7a2.jpg', 'local', '242bd6a2e456423c90eb642742b5da33~tplv-aphluv4xwc-origin-image', 1, '2026-03-23 15:23:18'),
	(3, 2, 'products/2/40f0f3aefdd84d95b54b0f3f10c44b57.png', 'local', 'ScreenShot_2026-03-16_202401_617', 2, '2026-03-23 15:23:29');
/*!40000 ALTER TABLE `product_images` ENABLE KEYS */;

-- 导出  表 ecom_db.product_reviews 结构
CREATE TABLE IF NOT EXISTS `product_reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `order_id` int(11) DEFAULT NULL,
  `rating` smallint(6) NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `reject_reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reviewer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_verified_purchase` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `order_id` (`order_id`),
  KEY `ix_product_reviews_product_id` (`product_id`),
  KEY `ix_product_reviews_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.product_reviews 的数据：0 rows
/*!40000 ALTER TABLE `product_reviews` DISABLE KEYS */;
/*!40000 ALTER TABLE `product_reviews` ENABLE KEYS */;

-- 导出  表 ecom_db.product_skus 结构
CREATE TABLE IF NOT EXISTS `product_skus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) NOT NULL,
  `sku_code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `compare_price` decimal(10,2) DEFAULT NULL,
  `stock` int(11) NOT NULL DEFAULT '0',
  `low_stock_threshold` int(11) NOT NULL DEFAULT '5',
  `variant_attrs` longtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `free_shipping` tinyint(1) NOT NULL DEFAULT '0',
  `weight_grams` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sku_code` (`sku_code`),
  KEY `ix_product_skus_product_id` (`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.product_skus 的数据：14 rows
/*!40000 ALTER TABLE `product_skus` DISABLE KEYS */;
INSERT INTO `product_skus` (`id`, `product_id`, `sku_code`, `price`, `compare_price`, `stock`, `low_stock_threshold`, `variant_attrs`, `is_active`, `free_shipping`, `weight_grams`, `created_at`, `updated_at`) VALUES
	(1, 1, 'P1', 1.00, 11.00, 110, 5, '{}', 1, 1, NULL, '2026-03-23 14:59:05', '2026-03-23 14:59:05'),
	(2, 1, 'P2', 2.00, 22.00, 111, 5, '{}', 1, 1, NULL, '2026-03-23 14:59:05', '2026-03-23 14:59:05'),
	(3, 2, 'RED-XXXL', 22.00, 44.00, 69, 5, '{"SIze": "XXXL", "Color": "red"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-24 18:15:22'),
	(4, 2, 'RED-XXL', 22.00, 44.00, 109, 5, '{"SIze": "XXL", "Color": "red"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-24 14:23:48'),
	(5, 2, 'RED-XL', 22.00, 44.00, 103, 5, '{"SIze": "XL", "Color": "red"}', 1, 1, NULL, '2026-03-23 15:23:10', '2026-03-24 17:37:42'),
	(6, 2, 'RED-L', 22.00, 44.00, 110, 5, '{"SIze": "L", "Color": "red"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-24 17:37:42'),
	(7, 2, 'GREEN-XXXL', 22.00, 44.00, 111, 5, '{"SIze": "XXXL", "Color": "green"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-23 15:23:10'),
	(8, 2, 'GREEN-XXL', 22.00, 44.00, 104, 5, '{"SIze": "XXL", "Color": "green"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-24 17:28:27'),
	(9, 2, 'GREEN-XL', 22.00, 44.00, 105, 5, '{"SIze": "XL", "Color": "green"}', 1, 1, NULL, '2026-03-23 15:23:10', '2026-03-24 15:54:23'),
	(10, 2, 'GREEN-L', 22.00, 44.00, 111, 5, '{"SIze": "L", "Color": "green"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-23 15:23:10'),
	(11, 2, 'BLACH-XXXL', 22.00, 44.00, 111, 5, '{"SIze": "XXXL", "Color": "blach"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-23 15:23:10'),
	(12, 2, 'BLACH-XXL', 22.00, 44.00, 111, 5, '{"SIze": "XXL", "Color": "blach"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-23 15:23:10'),
	(13, 2, 'BLACH-XL', 22.00, 44.00, 111, 5, '{"SIze": "XL", "Color": "blach"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-23 15:23:10'),
	(14, 2, 'BLACH-L', 22.00, 44.00, 109, 5, '{"SIze": "L", "Color": "blach"}', 1, 0, NULL, '2026-03-23 15:23:10', '2026-03-24 15:56:24');
/*!40000 ALTER TABLE `product_skus` ENABLE KEYS */;

-- 导出  表 ecom_db.refunds 结构
CREATE TABLE IF NOT EXISTS `refunds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `payment_id` int(11) NOT NULL,
  `provider_refund_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `amount` decimal(10,2) NOT NULL,
  `reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `processed_by` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `payment_id` (`payment_id`),
  KEY `processed_by` (`processed_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.refunds 的数据：0 rows
/*!40000 ALTER TABLE `refunds` DISABLE KEYS */;
/*!40000 ALTER TABLE `refunds` ENABLE KEYS */;

-- 导出  表 ecom_db.review_media 结构
CREATE TABLE IF NOT EXISTS `review_media` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `review_id` int(11) NOT NULL,
  `url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `storage_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'local',
  `media_type` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `sort_order` smallint(6) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `review_id` (`review_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.review_media 的数据：0 rows
/*!40000 ALTER TABLE `review_media` DISABLE KEYS */;
/*!40000 ALTER TABLE `review_media` ENABLE KEYS */;

-- 导出  表 ecom_db.shipments 结构
CREATE TABLE IF NOT EXISTS `shipments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `carrier_id` int(11) NOT NULL,
  `tracking_no` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shipped_by` int(11) DEFAULT NULL,
  `shipped_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `note` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`),
  KEY `carrier_id` (`carrier_id`),
  KEY `shipped_by` (`shipped_by`),
  KEY `ix_shipments_order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.shipments 的数据：0 rows
/*!40000 ALTER TABLE `shipments` DISABLE KEYS */;
/*!40000 ALTER TABLE `shipments` ENABLE KEYS */;

-- 导出  表 ecom_db.shipping_regions 结构
CREATE TABLE IF NOT EXISTS `shipping_regions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_shipping_regions_country` (`country_code`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.shipping_regions 的数据：68 rows
/*!40000 ALTER TABLE `shipping_regions` DISABLE KEYS */;
INSERT INTO `shipping_regions` (`id`, `country_code`, `state_code`, `enabled`, `created_at`, `updated_at`) VALUES
	(1, 'US', 'AL', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'US', 'AR', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'US', 'AZ', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'US', 'CA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'US', 'CO', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(6, 'US', 'CT', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(7, 'US', 'DE', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(8, 'US', 'FL', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(9, 'US', 'GA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(10, 'US', 'IA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(11, 'US', 'ID', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(12, 'US', 'IL', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(13, 'US', 'IN', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(14, 'US', 'KS', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(15, 'US', 'KY', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(16, 'US', 'LA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(17, 'US', 'MA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(18, 'US', 'MD', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(19, 'US', 'ME', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(20, 'US', 'MI', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(21, 'US', 'MN', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(22, 'US', 'MO', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(23, 'US', 'MS', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(24, 'US', 'MT', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(25, 'US', 'NC', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(26, 'US', 'ND', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(27, 'US', 'NE', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(28, 'US', 'NH', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(29, 'US', 'NJ', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(30, 'US', 'NM', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(31, 'US', 'NV', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(32, 'US', 'NY', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(33, 'US', 'OH', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(34, 'US', 'OK', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(35, 'US', 'OR', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(36, 'US', 'PA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(37, 'US', 'RI', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(38, 'US', 'SC', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(39, 'US', 'SD', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(40, 'US', 'TN', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(41, 'US', 'TX', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(42, 'US', 'UT', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(43, 'US', 'VA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(44, 'US', 'VT', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(45, 'US', 'WA', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(46, 'US', 'WI', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(47, 'US', 'WV', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(48, 'US', 'WY', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(49, 'US', 'DC', 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(50, 'US', 'AK', 0, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(51, 'US', 'HI', 0, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(52, 'DE', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(53, 'FR', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(54, 'IT', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(55, 'ES', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(56, 'NL', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(57, 'BE', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(58, 'AT', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(59, 'PT', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(60, 'SE', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(61, 'DK', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(62, 'FI', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(63, 'NO', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(64, 'PL', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(65, 'CZ', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(66, 'HU', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(67, 'GB', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(68, 'CA', NULL, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `shipping_regions` ENABLE KEYS */;

-- 导出  表 ecom_db.shipping_rules 结构
CREATE TABLE IF NOT EXISTS `shipping_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `zone_id` int(11) NOT NULL,
  `shipping_fee` decimal(10,2) NOT NULL,
  `free_shipping_threshold` decimal(10,2) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `zone_id` (`zone_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.shipping_rules 的数据：5 rows
/*!40000 ALTER TABLE `shipping_rules` DISABLE KEYS */;
INSERT INTO `shipping_rules` (`id`, `zone_id`, `shipping_fee`, `free_shipping_threshold`, `is_active`, `created_at`, `updated_at`) VALUES
	(1, 1, 5.99, 10.00, 1, '2026-03-17 07:59:00', '2026-03-23 20:45:20'),
	(2, 2, 8.99, 70.00, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 3, 7.99, 60.00, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 4, 9.99, 70.00, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 5, 14.99, 100.00, 1, '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `shipping_rules` ENABLE KEYS */;

-- 导出  表 ecom_db.shipping_zones 结构
CREATE TABLE IF NOT EXISTS `shipping_zones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.shipping_zones 的数据：5 rows
/*!40000 ALTER TABLE `shipping_zones` DISABLE KEYS */;
INSERT INTO `shipping_zones` (`id`, `name`, `created_at`, `updated_at`) VALUES
	(1, 'US Mainland', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'Europe', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'United Kingdom', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'Canada', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'International', '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `shipping_zones` ENABLE KEYS */;

-- 导出  表 ecom_db.shipping_zone_regions 结构
CREATE TABLE IF NOT EXISTS `shipping_zone_regions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `zone_id` int(11) NOT NULL,
  `country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_shipping_zone_regions_zone_id` (`zone_id`),
  KEY `ix_shipping_zone_regions_country_code` (`country_code`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.shipping_zone_regions 的数据：18 rows
/*!40000 ALTER TABLE `shipping_zone_regions` DISABLE KEYS */;
INSERT INTO `shipping_zone_regions` (`id`, `zone_id`, `country_code`) VALUES
	(1, 1, 'US'),
	(2, 2, 'DE'),
	(3, 2, 'FR'),
	(4, 2, 'IT'),
	(5, 2, 'ES'),
	(6, 2, 'NL'),
	(7, 2, 'BE'),
	(8, 2, 'AT'),
	(9, 2, 'PT'),
	(10, 2, 'SE'),
	(11, 2, 'DK'),
	(12, 2, 'FI'),
	(13, 2, 'NO'),
	(14, 2, 'PL'),
	(15, 2, 'CZ'),
	(16, 2, 'HU'),
	(17, 3, 'GB'),
	(18, 4, 'CA');
/*!40000 ALTER TABLE `shipping_zone_regions` ENABLE KEYS */;

-- 导出  表 ecom_db.site_settings 结构
CREATE TABLE IF NOT EXISTS `site_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text COLLATE utf8mb4_unicode_ci,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `setting_key` (`setting_key`),
  KEY `ix_site_settings_key` (`setting_key`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.site_settings 的数据：15 rows
/*!40000 ALTER TABLE `site_settings` DISABLE KEYS */;
INSERT INTO `site_settings` (`id`, `setting_key`, `setting_value`, `description`, `created_at`, `updated_at`) VALUES
	(1, 'site_name', 'My Store', 'Store display name', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(2, 'site_url', 'https://example.com', 'Canonical site URL', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(3, 'meta_title', 'My Store — Official Site', 'Default meta title', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(4, 'meta_description', 'Shop our products.', 'Default meta description', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(5, 'og_image', '', 'Default Open Graph image URL', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(6, 'google_analytics_id', '', 'Google Analytics measurement ID', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(7, 'robots_txt', 'User-agent: *\nAllow: /\nSitemap: https://example.com/sitemap.xml', 'robots.txt content', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(8, 'contact_whatsapp', '', 'WhatsApp contact URL or number', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(9, 'contact_facebook', '', 'Facebook page URL', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(10, 'contact_telegram', '', 'Telegram username or URL', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(11, 'contact_email', 'support@example.com', 'Support email address', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(12, 'review_auto_approve_threshold', '3', 'Reviews >= this rating auto-approve (0 = all manual)', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(13, 'currency', 'USD', 'Store currency (fixed)', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(14, 'languages', 'en,es', 'Supported language codes', '2026-03-17 07:59:00', '2026-03-17 07:59:00'),
	(15, 'default_language', 'en', 'Default language code', '2026-03-17 07:59:00', '2026-03-17 07:59:00');
/*!40000 ALTER TABLE `site_settings` ENABLE KEYS */;

-- 导出  表 ecom_db.tax_rules 结构
CREATE TABLE IF NOT EXISTS `tax_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tax_rate` decimal(5,4) NOT NULL,
  `tax_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Sales Tax',
  `apply_to_shipping` tinyint(1) NOT NULL DEFAULT '0',
  `category_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `ix_tax_rules_country` (`country_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.tax_rules 的数据：0 rows
/*!40000 ALTER TABLE `tax_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `tax_rules` ENABLE KEYS */;

-- 导出  表 ecom_db.users 结构
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `language_code` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'en',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'customer',
  `is_guest` tinyint(1) NOT NULL DEFAULT '0',
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `agree_terms` tinyint(1) NOT NULL DEFAULT '0',
  `agreed_at` datetime DEFAULT NULL,
  `avatar_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `ix_users_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.users 的数据：1 rows
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`, `email`, `password_hash`, `full_name`, `phone`, `language_code`, `role`, `is_guest`, `is_active`, `agree_terms`, `agreed_at`, `avatar_url`, `created_at`, `updated_at`) VALUES
	(1, 'zhanggold814@gmail.com', '$2b$12$yJyrjL886rlcuuSb7UQjdeltXvT18tQssESZe5E6lp0sMmnz0lX8K', NULL, NULL, 'en', 'customer', 0, 1, 1, '2026-03-23 11:21:38', NULL, '2026-03-23 19:21:37', '2026-03-23 19:21:37');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;

-- 导出  表 ecom_db.user_addresses 结构
CREATE TABLE IF NOT EXISTS `user_addresses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country_code` varchar(3) COLLATE utf8mb4_unicode_ci NOT NULL,
  `state_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address_line1` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `address_line2` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `postal_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_default` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_user_addresses_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.user_addresses 的数据：2 rows
/*!40000 ALTER TABLE `user_addresses` DISABLE KEYS */;
INSERT INTO `user_addresses` (`id`, `user_id`, `full_name`, `phone`, `country_code`, `state_code`, `state_name`, `city`, `address_line1`, `address_line2`, `postal_code`, `is_default`, `created_at`, `updated_at`) VALUES
	(2, 1, 'Morrie green', '+8616675345612', 'US', 'AL', '', 'Shenzhen', 'Longgang', 'Bantian', '512000', 1, '2026-03-24 10:11:39', '2026-03-24 11:09:35'),
	(10, 1, 'Morrie green', '+8616675345612', 'US', 'AL', '', 'Shenzhen', 'Longgang', 'Bantian', '512000', 0, '2026-03-24 15:56:24', '2026-03-24 15:56:24');
/*!40000 ALTER TABLE `user_addresses` ENABLE KEYS */;

-- 导出  表 ecom_db.wishlist 结构
CREATE TABLE IF NOT EXISTS `wishlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `ix_wishlist_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 正在导出表  ecom_db.wishlist 的数据：0 rows
/*!40000 ALTER TABLE `wishlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `wishlist` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;