create table "public"."addition_fact_performances" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" uuid not null,
    "fact_key" text not null,
    "total_attempts" integer default 0,
    "correct_attempts" integer default 0,
    "total_response_time_ms" bigint default 0,
    "fastest_response_ms" integer,
    "slowest_response_ms" integer,
    "last_attempted" timestamp with time zone,
    "mastery_level" text default 'learning'::text,
    "created_at" timestamp with time zone default now(),
    "updated_at" timestamp with time zone default now()
);


alter table "public"."addition_fact_performances" enable row level security;

CREATE UNIQUE INDEX addition_fact_performances_pkey ON public.addition_fact_performances USING btree (id);

CREATE UNIQUE INDEX addition_fact_performances_user_fact_unique ON public.addition_fact_performances USING btree (user_id, fact_key);

CREATE INDEX idx_addition_fact_performances_last_attempted ON public.addition_fact_performances USING btree (user_id, last_attempted);

CREATE INDEX idx_addition_fact_performances_mastery ON public.addition_fact_performances USING btree (user_id, mastery_level);

CREATE INDEX idx_addition_fact_performances_user_id ON public.addition_fact_performances USING btree (user_id);

alter table "public"."addition_fact_performances" add constraint "addition_fact_performances_pkey" PRIMARY KEY using index "addition_fact_performances_pkey";

alter table "public"."addition_fact_performances" add constraint "addition_fact_performances_user_fact_unique" UNIQUE using index "addition_fact_performances_user_fact_unique";

alter table "public"."addition_fact_performances" add constraint "addition_fact_performances_user_id_fkey" FOREIGN KEY (user_id) REFERENCES user_profiles(id) ON DELETE CASCADE not valid;

alter table "public"."addition_fact_performances" validate constraint "addition_fact_performances_user_id_fkey";

alter table "public"."addition_fact_performances" add constraint "positive_times" CHECK ((total_response_time_ms >= 0)) not valid;

alter table "public"."addition_fact_performances" validate constraint "positive_times";

alter table "public"."addition_fact_performances" add constraint "valid_attempts" CHECK ((correct_attempts <= total_attempts)) not valid;

alter table "public"."addition_fact_performances" validate constraint "valid_attempts";

alter table "public"."addition_fact_performances" add constraint "valid_mastery_level" CHECK ((mastery_level = ANY (ARRAY['learning'::text, 'practicing'::text, 'mastered'::text]))) not valid;

alter table "public"."addition_fact_performances" validate constraint "valid_mastery_level";

alter table "public"."addition_fact_performances" add constraint "valid_response_times" CHECK ((((fastest_response_ms IS NULL) AND (slowest_response_ms IS NULL)) OR ((fastest_response_ms IS NOT NULL) AND (slowest_response_ms IS NOT NULL) AND (fastest_response_ms <= slowest_response_ms)))) not valid;

alter table "public"."addition_fact_performances" validate constraint "valid_response_times";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$function$
;

grant delete on table "public"."addition_fact_performances" to "anon";

grant insert on table "public"."addition_fact_performances" to "anon";

grant references on table "public"."addition_fact_performances" to "anon";

grant select on table "public"."addition_fact_performances" to "anon";

grant trigger on table "public"."addition_fact_performances" to "anon";

grant truncate on table "public"."addition_fact_performances" to "anon";

grant update on table "public"."addition_fact_performances" to "anon";

grant delete on table "public"."addition_fact_performances" to "authenticated";

grant insert on table "public"."addition_fact_performances" to "authenticated";

grant references on table "public"."addition_fact_performances" to "authenticated";

grant select on table "public"."addition_fact_performances" to "authenticated";

grant trigger on table "public"."addition_fact_performances" to "authenticated";

grant truncate on table "public"."addition_fact_performances" to "authenticated";

grant update on table "public"."addition_fact_performances" to "authenticated";

grant delete on table "public"."addition_fact_performances" to "service_role";

grant insert on table "public"."addition_fact_performances" to "service_role";

grant references on table "public"."addition_fact_performances" to "service_role";

grant select on table "public"."addition_fact_performances" to "service_role";

grant trigger on table "public"."addition_fact_performances" to "service_role";

grant truncate on table "public"."addition_fact_performances" to "service_role";

grant update on table "public"."addition_fact_performances" to "service_role";

create policy "Users can insert own fact performances"
on "public"."addition_fact_performances"
as permissive
for insert
to public
with check ((auth.uid() = user_id));


create policy "Users can update own fact performances"
on "public"."addition_fact_performances"
as permissive
for update
to public
using ((auth.uid() = user_id));


create policy "Users can view own fact performances"
on "public"."addition_fact_performances"
as permissive
for select
to public
using ((auth.uid() = user_id));


CREATE TRIGGER update_addition_fact_performances_updated_at BEFORE UPDATE ON public.addition_fact_performances FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


