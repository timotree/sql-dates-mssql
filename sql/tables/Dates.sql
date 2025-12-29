CREATE TABLE Times.Dates
(
    DateID int IDENTITY(1, 1) NOT NULL
    ,DateDate date NOT NULL
    ,DateYear smallint NOT NULL
    ,DateMonth tinyint NOT NULL
    ,DateDay tinyint NOT NULL
    ,DateDayOfWeek tinyint NOT NULL
    ,IsLastDayOfMonth bit NOT NULL
    ,IsWeekend bit NOT NULL
    ,IsHoliday bit NOT NULL
    ,IsWorkDay bit NOT NULL
    ,IsPayDay bit NOT NULL
    ,DayOfWeekName varchar(9) NOT NULL
    ,NameOfMonth varchar(9) NOT NULL
    ,CYQuarter tinyint NOT NULL
    ,CYDay smallint NOT NULL
    ,CYWeek tinyint NOT NULL
    ,CONSTRAINT PK_Dates
        PRIMARY KEY (DateID)
    ,CONSTRAINT UK_Dates_DateDate
        UNIQUE (DateDate)
);
