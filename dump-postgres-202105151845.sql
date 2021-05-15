PGDMP     1    -                y            postgres    13.3    13.3 !    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    13442    postgres    DATABASE     e   CREATE DATABASE postgres WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'Russian_Russia.1251';
    DROP DATABASE postgres;
                postgres    false            �           0    0    DATABASE postgres    COMMENT     N   COMMENT ON DATABASE postgres IS 'default administrative connection database';
                   postgres    false    3027                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
                postgres    false            �           0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                   postgres    false    4            �            1259    16425    hackathon_seq    SEQUENCE     v   CREATE SEQUENCE public.hackathon_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.hackathon_seq;
       public          postgres    false    4            �            1259    16435    meeting_participants    TABLE     �   CREATE TABLE public.meeting_participants (
    id integer DEFAULT nextval('public.hackathon_seq'::regclass) NOT NULL,
    is_accept boolean,
    user_id integer,
    rating integer
);
 (   DROP TABLE public.meeting_participants;
       public         heap    postgres    false    204    4            �            1259    16433    meeting_participants_id_seq    SEQUENCE     �   CREATE SEQUENCE public.meeting_participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.meeting_participants_id_seq;
       public          postgres    false    4    206            �           0    0    meeting_participants_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.meeting_participants_id_seq OWNED BY public.meeting_participants.id;
          public          postgres    false    205            �            1259    16409    meets    TABLE     >  CREATE TABLE public.meets (
    status character varying(100),
    start_date timestamp without time zone,
    first_user integer,
    id integer DEFAULT nextval('public.hackathon_seq'::regclass) NOT NULL,
    second_user integer,
    first_user_accept boolean,
    second_user_accept boolean,
    notified boolean
);
    DROP TABLE public.meets;
       public         heap    postgres    false    204    4            �            1259    16448    meets_meeting_participants    TABLE     v   CREATE TABLE public.meets_meeting_participants (
    meet_id integer NOT NULL,
    participant_id integer NOT NULL
);
 .   DROP TABLE public.meets_meeting_participants;
       public         heap    postgres    false    4            �            1259    16406    user_id_seq    SEQUENCE     t   CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.user_id_seq;
       public          postgres    false    4            �            1259    16394    users    TABLE       CREATE TABLE public.users (
    id integer DEFAULT nextval('public.user_id_seq'::regclass) NOT NULL,
    firstname character varying(100),
    lastname character varying(100),
    "position" character varying(100),
    sex boolean,
    telegram_id integer
);
    DROP TABLE public.users;
       public         heap    postgres    false    202    4            �          0    16435    meeting_participants 
   TABLE DATA           N   COPY public.meeting_participants (id, is_accept, user_id, rating) FROM stdin;
    public          postgres    false    206            �          0    16409    meets 
   TABLE DATA           �   COPY public.meets (status, start_date, first_user, id, second_user, first_user_accept, second_user_accept, notified) FROM stdin;
    public          postgres    false    203            �          0    16448    meets_meeting_participants 
   TABLE DATA           M   COPY public.meets_meeting_participants (meet_id, participant_id) FROM stdin;
    public          postgres    false    207            �          0    16394    users 
   TABLE DATA           V   COPY public.users (id, firstname, lastname, "position", sex, telegram_id) FROM stdin;
    public          postgres    false    201            �           0    0    hackathon_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.hackathon_seq', 100, true);
          public          postgres    false    204            �           0    0    meeting_participants_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.meeting_participants_id_seq', 1, false);
          public          postgres    false    205            �           0    0    user_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.user_id_seq', 13, true);
          public          postgres    false    202            =           2606    16441 ,   meeting_participants meeting_participants_pk 
   CONSTRAINT     j   ALTER TABLE ONLY public.meeting_participants
    ADD CONSTRAINT meeting_participants_pk PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.meeting_participants DROP CONSTRAINT meeting_participants_pk;
       public            postgres    false    206            ?           2606    16452 :   meets_meeting_participants meets_meeting_participants_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.meets_meeting_participants
    ADD CONSTRAINT meets_meeting_participants_pkey PRIMARY KEY (meet_id, participant_id);
 d   ALTER TABLE ONLY public.meets_meeting_participants DROP CONSTRAINT meets_meeting_participants_pkey;
       public            postgres    false    207    207            :           2606    16413    meets meets_pk 
   CONSTRAINT     L   ALTER TABLE ONLY public.meets
    ADD CONSTRAINT meets_pk PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.meets DROP CONSTRAINT meets_pk;
       public            postgres    false    203            7           2606    16398    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    201            ;           1259    16439    meeting_participants_id_uindex    INDEX     d   CREATE UNIQUE INDEX meeting_participants_id_uindex ON public.meeting_participants USING btree (id);
 2   DROP INDEX public.meeting_participants_id_uindex;
       public            postgres    false    206            8           1259    16424    meets_id_uindex    INDEX     F   CREATE UNIQUE INDEX meets_id_uindex ON public.meets USING btree (id);
 #   DROP INDEX public.meets_id_uindex;
       public            postgres    false    203            B           2606    16442 5   meeting_participants meeting_participants_users_id_fk    FK CONSTRAINT     �   ALTER TABLE ONLY public.meeting_participants
    ADD CONSTRAINT meeting_participants_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id);
 _   ALTER TABLE ONLY public.meeting_participants DROP CONSTRAINT meeting_participants_users_id_fk;
       public          postgres    false    206    2871    201            C           2606    16453 B   meets_meeting_participants meets_meeting_participants_meet_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.meets_meeting_participants
    ADD CONSTRAINT meets_meeting_participants_meet_id_fkey FOREIGN KEY (meet_id) REFERENCES public.meets(id);
 l   ALTER TABLE ONLY public.meets_meeting_participants DROP CONSTRAINT meets_meeting_participants_meet_id_fkey;
       public          postgres    false    207    203    2874            D           2606    16458 I   meets_meeting_participants meets_meeting_participants_participant_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.meets_meeting_participants
    ADD CONSTRAINT meets_meeting_participants_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES public.meeting_participants(id);
 s   ALTER TABLE ONLY public.meets_meeting_participants DROP CONSTRAINT meets_meeting_participants_participant_id_fkey;
       public          postgres    false    207    206    2875            @           2606    16414    meets meets_users_id_fk    FK CONSTRAINT     y   ALTER TABLE ONLY public.meets
    ADD CONSTRAINT meets_users_id_fk FOREIGN KEY (first_user) REFERENCES public.users(id);
 A   ALTER TABLE ONLY public.meets DROP CONSTRAINT meets_users_id_fk;
       public          postgres    false    203    2871    201            A           2606    16419    meets meets_users_id_fk_2    FK CONSTRAINT     |   ALTER TABLE ONLY public.meets
    ADD CONSTRAINT meets_users_id_fk_2 FOREIGN KEY (second_user) REFERENCES public.users(id);
 C   ALTER TABLE ONLY public.meets DROP CONSTRAINT meets_users_id_fk_2;
       public          postgres    false    2871    201    203            �   =   x��4�,�44�4䲰��9��,�8�@b1~\�� �1�i�5�(1-
, F�1z\\\ �%      �   s   x�}�A� �����4@��VX4i�ح���S�DWm2�y3)/�gɉ���v92J�N�`(NK{��TK���D+E4ЫN�����x"�ѱ�nu��
�M�?^l��F�)R      �   0   x�%Ź  �x�t�?��H�ؤ6&E�.곙%�s:#���Sl_�b      �   f   x�34�0�;.6]l����NN���TN�ԲԜ���"�?NK##KS.Cc�.6\l������.컰�7]�pa7�F�gjdjh`df����� �.�      !    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    13442    postgres    DATABASE     e   CREATE DATABASE postgres WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'Russian_Russia.1251';
    DROP DATABASE postgres;
                postgres    false            �           0    0    DATABASE postgres    COMMENT     N   COMMENT ON DATABASE postgres IS 'default administrative connection database';
                   postgres    false    3027                        2615    2200    public    SCHEMA        CREATE SCHEMA public;
    DROP SCHEMA public;
                postgres    false            �           0    0    SCHEMA public    COMMENT     6   COMMENT ON SCHEMA public IS 'standard public schema';
                   postgres    false    4            �            1259    16425    hackathon_seq    SEQUENCE     v   CREATE SEQUENCE public.hackathon_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.hackathon_seq;
       public          postgres    false    4            �            1259    16435    meeting_participants    TABLE     �   CREATE TABLE public.meeting_participants (
    id integer DEFAULT nextval('public.hackathon_seq'::regclass) NOT NULL,
    is_accept boolean,
    user_id integer,
    rating integer
);
 (   DROP TABLE public.meeting_participants;
       public         heap    postgres    false    204    4            �            1259    16433    meeting_participants_id_seq    SEQUENCE     �   CREATE SEQUENCE public.meeting_participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.meeting_participants_id_seq;
       public          postgres    false    4    206            �           0    0    meeting_participants_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.meeting_participants_id_seq OWNED BY public.meeting_participants.id;
          public          postgres    false    205            �            1259    16409    meets    TABLE     >  CREATE TABLE public.meets (
    status character varying(100),
    start_date timestamp without time zone,
    first_user integer,
    id integer DEFAULT nextval('public.hackathon_seq'::regclass) NOT NULL,
    second_user integer,
    first_user_accept boolean,
    second_user_accept boolean,
    notified boolean
);
    DROP TABLE public.meets;
       public         heap    postgres    false    204    4            �            1259    16448    meets_meeting_participants    TABLE     v   CREATE TABLE public.meets_meeting_participants (
    meet_id integer NOT NULL,
    participant_id integer NOT NULL
);
 .   DROP TABLE public.meets_meeting_participants;
       public         heap    postgres    false    4            �            1259    16406    user_id_seq    SEQUENCE     t   CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 "   DROP SEQUENCE public.user_id_seq;
       public          postgres    false    4            �            1259    16394    users    TABLE       CREATE TABLE public.users (
    id integer DEFAULT nextval('public.user_id_seq'::regclass) NOT NULL,
    firstname character varying(100),
    lastname character varying(100),
    "position" character varying(100),
    sex boolean,
    telegram_id integer
);
    DROP TABLE public.users;
       public         heap    postgres    false    202    4            �          0    16435    meeting_participants 
   TABLE DATA           N   COPY public.meeting_participants (id, is_accept, user_id, rating) FROM stdin;
    public          postgres    false    206   �       �          0    16409    meets 
   TABLE DATA           �   COPY public.meets (status, start_date, first_user, id, second_user, first_user_accept, second_user_accept, notified) FROM stdin;
    public          postgres    false    203   G        �          0    16448    meets_meeting_participants 
   TABLE DATA           M   COPY public.meets_meeting_participants (meet_id, participant_id) FROM stdin;
    public          postgres    false    207   }        �          0    16394    users 
   TABLE DATA           V   COPY public.users (id, firstname, lastname, "position", sex, telegram_id) FROM stdin;
    public          postgres    false    201   :        �           0    0    hackathon_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.hackathon_seq', 100, true);
          public          postgres    false    204            �           0    0    meeting_participants_id_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.meeting_participants_id_seq', 1, false);
          public          postgres    false    205            �           0    0    user_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.user_id_seq', 13, true);
          public          postgres    false    202            =           2606    16441 ,   meeting_participants meeting_participants_pk 
   CONSTRAINT     j   ALTER TABLE ONLY public.meeting_participants
    ADD CONSTRAINT meeting_participants_pk PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.meeting_participants DROP CONSTRAINT meeting_participants_pk;
       public            postgres    false    206            ?           2606    16452 :   meets_meeting_participants meets_meeting_participants_pkey 
   CONSTRAINT     �   ALTER TABLE ONLY public.meets_meeting_participants
    ADD CONSTRAINT meets_meeting_participants_pkey PRIMARY KEY (meet_id, participant_id);
 d   ALTER TABLE ONLY public.meets_meeting_participants DROP CONSTRAINT meets_meeting_participants_pkey;
       public            postgres    false    207    207            :           2606    16413    meets meets_pk 
   CONSTRAINT     L   ALTER TABLE ONLY public.meets
    ADD CONSTRAINT meets_pk PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.meets DROP CONSTRAINT meets_pk;
       public            postgres    false    203            7           2606    16398    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    201            ;           1259    16439    meeting_participants_id_uindex    INDEX     d   CREATE UNIQUE INDEX meeting_participants_id_uindex ON public.meeting_participants USING btree (id);
 2   DROP INDEX public.meeting_participants_id_uindex;
       public            postgres    false    206            8           1259    16424    meets_id_uindex    INDEX     F   CREATE UNIQUE INDEX meets_id_uindex ON public.meets USING btree (id);
 #   DROP INDEX public.meets_id_uindex;
       public            postgres    false    203            B           2606    16442 5   meeting_participants meeting_participants_users_id_fk    FK CONSTRAINT     �   ALTER TABLE ONLY public.meeting_participants
    ADD CONSTRAINT meeting_participants_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id);
 _   ALTER TABLE ONLY public.meeting_participants DROP CONSTRAINT meeting_participants_users_id_fk;
       public          postgres    false    206    2871    201            C           2606    16453 B   meets_meeting_participants meets_meeting_participants_meet_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.meets_meeting_participants
    ADD CONSTRAINT meets_meeting_participants_meet_id_fkey FOREIGN KEY (meet_id) REFERENCES public.meets(id);
 l   ALTER TABLE ONLY public.meets_meeting_participants DROP CONSTRAINT meets_meeting_participants_meet_id_fkey;
       public          postgres    false    207    203    2874            D           2606    16458 I   meets_meeting_participants meets_meeting_participants_participant_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.meets_meeting_participants
    ADD CONSTRAINT meets_meeting_participants_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES public.meeting_participants(id);
 s   ALTER TABLE ONLY public.meets_meeting_participants DROP CONSTRAINT meets_meeting_participants_participant_id_fkey;
       public          postgres    false    207    206    2875            @           2606    16414    meets meets_users_id_fk    FK CONSTRAINT     y   ALTER TABLE ONLY public.meets
    ADD CONSTRAINT meets_users_id_fk FOREIGN KEY (first_user) REFERENCES public.users(id);
 A   ALTER TABLE ONLY public.meets DROP CONSTRAINT meets_users_id_fk;
       public          postgres    false    203    2871    201            A           2606    16419    meets meets_users_id_fk_2    FK CONSTRAINT     |   ALTER TABLE ONLY public.meets
    ADD CONSTRAINT meets_users_id_fk_2 FOREIGN KEY (second_user) REFERENCES public.users(id);
 C   ALTER TABLE ONLY public.meets DROP CONSTRAINT meets_users_id_fk_2;
       public          postgres    false    2871    201    203           