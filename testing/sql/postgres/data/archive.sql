CREATE SCHEMA daiquiri_archive;

CREATE TABLE "daiquiri_archive"."files" (
    "id" char(36) primary key not null,
    "timestamp" timestamp not null,
    "file" varchar(32) not null,
    "collection" varchar(32) not null,
    "path" text not null,
    "ra" double precision not null,
    "dec" double precision not null
);

GRANT USAGE ON SCHEMA daiquiri_archive TO daiquiri_data;
GRANT SELECT ON ALL TABLES IN SCHEMA daiquiri_archive TO daiquiri_data;

INSERT INTO daiquiri_archive.files VALUES
('074fec76-6143-4d58-a1f6-a7e8c23af15e', '2017-10-01 00:00:00', 'images/image_01.jpg', 'c01', 'images/image_01.jpg', 5.810915172365783, -27.665464907831577),
('c5e61e94-767d-4a44-9fea-1f1f36318fbe', '2017-10-02 00:00:00', 'images/image_02.jpg', 'c02', 'images/image_02.jpg', 70.38985348435354, 43.43851902099498),
('03a4b87f-77dc-4004-903b-6726f4f18059', '2017-10-03 00:00:00', 'images/image_03.jpg', 'c03', 'images/image_03.jpg', -51.20680382696266, 10.389770122481512),
('48d7dd8c-d8d2-4653-af4a-d3baf3a50042', '2017-10-04 00:00:00', 'images/image_04.jpg', 'c04', 'images/image_04.jpg', 14.240230151343926, 32.84081167256645),
('0e16c9e9-d8b6-4850-b205-c51330b46195', '2017-10-05 00:00:00', 'images/image_05.jpg', 'c05', 'images/image_05.jpg', -36.386151594173676, 14.15371103822735),
('802af425-3029-4569-bf01-079af0c6f0eb', '2017-10-06 00:00:00', 'images/image_06.jpg', 'c06', 'images/image_06.jpg', -38.94798481900796, 24.039302526743597),
('fb120128-42b3-4845-9df9-d9a0227a9ef5', '2017-10-07 00:00:00', 'images/image_07.jpg', 'c07', 'images/image_07.jpg', -25.560533372296792, -28.05562075939341),
('27b2429c-db3f-489e-ad33-6809e90a894c', '2017-10-08 00:00:00', 'images/image_08.jpg', 'c08', 'images/image_08.jpg', 77.15147383524092, 27.857419507153956),
('04792293-6fd7-4fa3-a582-ec558e8a611e', '2017-10-09 00:00:00', 'images/image_09.jpg', 'c09', 'images/image_09.jpg', 36.9644420870539, -14.191961918609898),
('901f37e1-88d2-4874-875b-1e7c76b31f3c', '2017-10-10 00:00:00', 'images/image_10.jpg', 'c10', 'images/image_10.jpg', 19.820181616474308, 30.651501628603008),
('35c7870f-66c8-4237-82d5-690f752a1854', '2017-10-11 00:00:00', 'images/image_11.jpg', 'c11', 'images/image_11.jpg', 3.7994195568881994, 27.113117136415102),
('c0280e84-3839-4be6-8398-bde9cbbdac9a', '2017-10-12 00:00:00', 'images/image_12.jpg', 'c12', 'images/image_12.jpg', -25.54879565853578, -11.476513538754203),
('721998c0-42ac-4573-8ba1-01fa67c69ab9', '2017-10-13 00:00:00', 'images/image_13.jpg', 'c13', 'images/image_13.jpg', 32.0775997501004, 38.234200704194166),
('643c5171-0b0b-456f-9810-cefe04694b6b', '2017-10-14 00:00:00', 'images/image_14.jpg', 'c14', 'images/image_14.jpg', 19.01628554701213, -36.27679445341637),
('c28a217c-9b47-4536-b254-d8cb68519f04', '2017-10-15 00:00:00', 'images/image_15.jpg', 'c15', 'images/image_15.jpg', 70.9290627119285, 22.807968406758317),
('fc625c67-a450-4825-9bb2-5903c2795f4b', '2017-10-16 00:00:00', 'images/image_16.jpg', 'c16', 'images/image_16.jpg', -7.594247482047745, -5.314390546254827),
('d3bd3a1e-dd71-40a3-a0d5-646b05e39744', '2017-10-17 00:00:00', 'images/image_17.jpg', 'c17', 'images/image_17.jpg', 55.64259801627556, 37.24334225877411),
('640150cb-034d-44b1-8733-fe87437af601', '2017-10-18 00:00:00', 'images/image_18.jpg', 'c18', 'images/image_18.jpg', -53.71728159795077, -30.8278755856589),
('0c4b60a0-c6a5-4182-87ae-4731a3c018ae', '2017-10-19 00:00:00', 'images/image_19.jpg', 'c19', 'images/image_19.jpg', -73.69079476954084, -5.0966694262774626),
('ef5c845a-a182-4b67-9638-52f54021bd46', '2017-10-20 00:00:00', 'images/image_20.jpg', 'c20', 'images/image_20.jpg', -5.439769572289155, -28.74445840920812),
('1b1812c3-2911-4a28-bff1-41ad45086d28', '2017-10-01 00:00:00', 'images/image_01.fits', 'c01', 'images/image_01.fits', 11.347043016704774, -31.734729779604628),
('95362abc-ad62-4403-b04c-8ea64e642d1d', '2017-10-02 00:00:00', 'images/image_02.fits', 'c02', 'images/image_02.fits', 80.21086353330674, 41.12289484864426),
('3699eb32-c91f-44e9-9a11-2bb3e62dc569', '2017-10-03 00:00:00', 'images/image_03.fits', 'c03', 'images/image_03.fits', 50.85702033098946, -20.677059588099503),
('8604b8f3-29d8-49e5-942b-147cef55ae60', '2017-10-04 00:00:00', 'images/image_04.fits', 'c04', 'images/image_04.fits', -68.61349041775959, -34.72936652794893),
('afbe0a4e-7fc5-4539-94db-ab60ffb925d0', '2017-10-05 00:00:00', 'images/image_05.fits', 'c05', 'images/image_05.fits', -21.071174649348773, -38.23753858439784),
('d75c4401-89f7-4b82-8966-64e6674b3102', '2017-10-06 00:00:00', 'images/image_06.fits', 'c06', 'images/image_06.fits', -42.39118487107844, -11.989023083261317),
('39fc0461-5c46-44c5-913d-72f08f538c58', '2017-10-07 00:00:00', 'images/image_07.fits', 'c07', 'images/image_07.fits', -83.83984163949403, -24.599417358023285),
('7818a184-bde6-4c95-96aa-a3064f2cdced', '2017-10-08 00:00:00', 'images/image_08.fits', 'c08', 'images/image_08.fits', -64.00046046961211, -27.822187511022744),
('a33a0b8b-e9dd-4544-97ee-36b8dddf1ba6', '2017-10-09 00:00:00', 'images/image_09.fits', 'c09', 'images/image_09.fits', -56.280553072201435, 19.414688932124545),
('5d20f223-8a53-47b8-aa73-725cc6184a0d', '2017-10-10 00:00:00', 'images/image_10.fits', 'c10', 'images/image_10.fits', -66.29294335605213, -9.810116481499605),
('715b29e5-4a00-4d33-9357-8117ca2ed7cf', '2017-10-11 00:00:00', 'images/image_11.fits', 'c11', 'images/image_11.fits', 76.85044027539051, 27.180858709769105),
('c1b788e9-87f3-417c-adb2-f88e70579a04', '2017-10-12 00:00:00', 'images/image_12.fits', 'c12', 'images/image_12.fits', 72.95424857003677, 5.64576789675947),
('b83f5e01-cd69-48a0-9997-3a058df944aa', '2017-10-13 00:00:00', 'images/image_13.fits', 'c13', 'images/image_13.fits', -89.54351840277283, 36.101323929843495),
('bef73423-863c-4a1f-9ec0-56a9ac4019ba', '2017-10-14 00:00:00', 'images/image_14.fits', 'c14', 'images/image_14.fits', -48.599726842349746, -26.18386448616631),
('3fee60b9-e78e-4974-9997-f5d80c884bcb', '2017-10-15 00:00:00', 'images/image_15.fits', 'c15', 'images/image_15.fits', 48.80191645584114, -26.249715964712397),
('dd45b27c-882d-4327-b908-86102a73a082', '2017-10-16 00:00:00', 'images/image_16.fits', 'c16', 'images/image_16.fits', 28.13704518997618, 1.490597236264013),
('36ffa771-9c23-4f8c-9c62-e27b1a3b001c', '2017-10-17 00:00:00', 'images/image_17.fits', 'c17', 'images/image_17.fits', -70.30745298228646, -1.1405154589016464),
('f1c3974f-9c14-4e64-a8c2-a7e7a2e05639', '2017-10-18 00:00:00', 'images/image_18.fits', 'c18', 'images/image_18.fits', -71.60346050383421, -27.935554707115326),
('92d9936a-8f7b-4501-a61c-96ceddcb469d', '2017-10-19 00:00:00', 'images/image_19.fits', 'c19', 'images/image_19.fits', 67.70930246685508, -19.813289604840673),
('3436066b-38ec-4ea2-9c59-81212104555a', '2017-10-20 00:00:00', 'images/image_20.fits', 'c20', 'images/image_20.fits', 59.53285933408349, 20.269240354748845);
