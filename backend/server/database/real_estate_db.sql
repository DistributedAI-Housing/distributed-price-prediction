-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 03, 2026 at 02:27 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `real_estate_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `predictions`
--

CREATE TABLE `predictions` (
  `id` int(11) NOT NULL,
  `price` double NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `user_id` int(11) NOT NULL,
  `proprety_type` varchar(50) NOT NULL,
  `surface` float NOT NULL,
  `bedroom` int(11) NOT NULL,
  `bathroom` int(11) NOT NULL,
  `address` varchar(255) NOT NULL,
  `city` varchar(100) NOT NULL,
  `principale` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `predictions`
--

INSERT INTO `predictions` (`id`, `price`, `created_at`, `user_id`, `proprety_type`, `surface`, `bedroom`, `bathroom`, `address`, `city`, `principale`) VALUES
(1, 4239622.816, '2025-12-18 23:52:19', 1, 'House', 120, 3, 0, '', '', ''),
(2, 4239622.816000001, '2025-12-18 23:56:12', 1, 'House', 120, 3, 0, '', '', ''),
(3, 4239622.816, '2025-12-19 14:13:48', 1, 'House', 120, 3, 0, '', '', ''),
(4, 4877070.344533334, '2025-12-19 14:15:32', 1, 'House', 166, 4, 0, '', '', ''),
(5, 4848613.808666666, '2025-12-19 14:16:24', 1, 'Apartment', 166, 4, 0, '', '', ''),
(6, 1759939.2621333334, '2025-12-19 14:17:02', 1, 'Apartment', 66, 2, 0, '', '', ''),
(7, 3870710.0856333333, '2025-12-19 14:18:24', 1, 'Apartment', 106, 2, 0, '', '', ''),
(8, 0, '2025-12-19 14:24:58', 1, 'Apartment', 106, 2, 1, '3870710.0856333333', 'Rabat', ''),
(9, 3870710.0856333333, '2025-12-19 14:28:22', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', ''),
(10, 3870710.0856333333, '2025-12-19 14:30:24', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(11, 3870710.0856333333, '2025-12-19 15:29:27', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(12, 3870710.0856333333, '2025-12-19 15:35:43', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(13, 3870710.0856333333, '2025-12-19 15:43:53', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(14, 3870710.0856333333, '2025-12-19 15:44:49', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(15, 3870710.0856333333, '2025-12-19 15:45:02', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(16, 3870710.0856333333, '2025-12-19 15:47:54', 1, 'Apartment', 106, 2, 1, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(17, 7780820.282399999, '2025-12-31 23:40:52', 4, 'Villa', 234, 3, 2, 'Marrakech', 'Marrakech', 'Marrakech'),
(18, 1772238.9579666667, '2025-12-31 23:43:54', 5, 'Apartment', 60, 2, 2, 'Rabat', 'Rabat', 'Rabat-Salé-Kénitra'),
(19, 4424727.6066000005, '2025-12-31 23:58:06', 5, 'Villa', 233, 3, 3, 'Agadir', 'Agadir', 'Agadir'),
(20, 5129819.9366666665, '2026-01-03 13:22:16', 5, 'Apartment', 143, 3, 2, 'Agdal', 'Rabat', 'Rabat-Salé-Kénitra');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `profile_image_path` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `password_hash`, `profile_image_path`, `created_at`) VALUES
(1, '', 'rim@example.com', '123456', NULL, '2025-12-18 23:51:37'),
(2, 'aya', 'ayaamer@gmail.com', 'scrypt:32768:8:1$BiVzCdz7Ndc73Ct1$e65a1e47b537ecb3cd020e6ba62fb09dfa81a1837f61391ee55ab1c9f5ed279730af3f1fdeb490236308ab7a2deee92127bb5842e8f0696ca4ebd60cbce96885', 'default.png', '2025-12-31 23:06:34'),
(3, 'rimbari', 'rimbari@gmail.com', 'scrypt:32768:8:1$rBSjC6zi7TmrCXXj$818516cf1f4b2a5a15c1beb2909daa1ee94ed78e15f214c9273404a17b107952bc16bc1262e45af896ac30e37731e42c42532f32012d170e52579e454a20a736', 'default_avatar.png', '2025-12-31 21:29:01'),
(4, 'RAYAN', 'rayan@gmail.com', 'scrypt:32768:8:1$nVKtwtrOPJ4Memq1$137d74ed86a7ff5da6df12f43392229dc2273f2fd0a3ee5deca3dce68da6672df679bd3a27f1788f8b9ff467faeb69fe392903333aed148588080b025b484ffc', 'default.png', '2025-12-31 23:18:21'),
(5, 'aya', 'aya23@gmail.com', 'scrypt:32768:8:1$5EYcnUXrBYmvpSdM$9bb71b24eae868da4255a7c564ac77c3d7c872bc0e89fae9c5146bee706347e71566e18dbcf5bd196523c245ff5977acafbac6de807b01758ea5739debebc63f', 'default.png', '2025-12-31 23:42:48');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `predictions`
--
ALTER TABLE `predictions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_user_id` (`user_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `predictions`
--
ALTER TABLE `predictions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `predictions`
--
ALTER TABLE `predictions`
  ADD CONSTRAINT `fk_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
