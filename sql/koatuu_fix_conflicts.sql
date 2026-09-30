USE [UPI_AGRO_WORK];
GO

DECLARE @Apply bit = 0;   -- 0 = тільки перегляд, 1 = виконати UPDATE

DROP TABLE IF EXISTS #fix;

CREATE TABLE #fix (
    KOATUU     varchar(10)   NOT NULL PRIMARY KEY,
    NewFarm    nvarchar(500) NOT NULL,
    NewVidd    nvarchar(200) NOT NULL
);
INSERT INTO #fix (KOATUU, NewFarm, NewVidd) VALUES
 ('0520886500', N'Філія "Кунянська"',    N'Гранів'),
 ('0520883000', N'Філія "Немирівська"',  N'Ситківці');

/* Перегляд: що зміниться */
SELECT d.KOATUU, d.CouncilName,
       d.Farm AS Old_Farm, f.NewFarm,
       d.[Відділення] AS Old_Vidd, f.NewVidd
FROM dbo.KoatuuDirectory d
JOIN #fix f ON f.KOATUU = d.KOATUU
WHERE d.Farm <> f.NewFarm OR ISNULL(d.[Відділення], N'') <> f.NewVidd;

-- Довідково: коди з файлу, яких немає в поточній базі (нічого оновлювати)
SELECT f.KOATUU AS Not_Found_In_Directory
FROM #fix f
WHERE NOT EXISTS (SELECT 1 FROM dbo.KoatuuDirectory d WHERE d.KOATUU = f.KOATUU);

SELECT KOATUU AS Not_Found_In_Directory
FROM (VALUES ('0520880900'), ('0520885600')) AS v(KOATUU)
WHERE NOT EXISTS (SELECT 1 FROM dbo.KoatuuDirectory d WHERE d.KOATUU = v.KOATUU);

IF @Apply = 1
BEGIN
    UPDATE d
       SET d.Farm = f.NewFarm,
           d.[Відділення] = f.NewVidd
    FROM dbo.KoatuuDirectory d
    JOIN #fix f ON f.KOATUU = d.KOATUU
    WHERE d.Farm <> f.NewFarm OR ISNULL(d.[Відділення], N'') <> f.NewVidd;

    SELECT @@ROWCOUNT AS UpdatedRows;
END
