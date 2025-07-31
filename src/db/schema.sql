CREATE TABLE public.habits
(
    "id" BIGINT,
    "name" VARCHAR(255),
    "from_t" TIME WITHOUT TIME ZONE,
    "to_t" TIME WITHOUT TIME ZONE
);


CREATE TABLE public.tasks
(
    "id" BIGINT,
    "name" VARCHAR(255),
    "deadline" DATE,
    "is_done" DATE
);


CREATE TABLE public.progress
(
    "id" BIGINT,
    "is_habit" boolean,
    "time" BIGINT,
    "date" DATE
);
