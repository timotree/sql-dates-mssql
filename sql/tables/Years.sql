CREATE TABLE Times.Years
(
    YearYear smallint NOT NULL
    ,TotalDays smallint NOT NULL
    ,WorkDays smallint NOT NULL
    ,Holidays tinyint NOT NULL
    ,WeekDays smallint NOT NULL
    ,WeekendDays smallint NOT NULL
    ,WorkHours smallint NOT NULL
    ,PayPeriods smallint NOT NULL
    ,IsLeap bit NOT NULL
    ,IsPresElection bit NOT NULL
    ,IsInauguration bit NOT NULL
    ,CONSTRAINT PK_Years
        PRIMARY KEY (YearYear)
);
