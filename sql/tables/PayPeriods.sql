CREATE TABLE Times.PayPeriods
(
    PayPeriodID int NOT NULL
    ,StartDate date NOT NULL
    ,EndDate date NOT NULL
    ,PPIndex int NOT NULL
    ,PPNumber tinyint NOT NULL
    ,YearStart char(4) NOT NULL
    ,YearEnd char(4) NOT NULL
    ,IsSplitYear bit NOT NULL
    ,Holidays tinyint NOT NULL
    ,WorkDaysInYearStart tinyint NOT NULL
    ,WorkDaysInYearEnd tinyint NOT NULL
    ,HoursInYearStart tinyint NOT NULL
    ,HoursInYearEnd tinyint NOT NULL
    ,PayDate date NOT NULL
    ,PayYear char(4) NOT NULL
    ,CONSTRAINT PK_PayPeriods
        PRIMARY KEY (PayPeriodID)
);
