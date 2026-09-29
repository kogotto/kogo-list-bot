--
-- PostgreSQL database dump
--

\restrict UIJur83vYnmYhLCNTOUTE9koXxtSiKTw6on5U2z9gjSqgCISFRd0mIxU6BsGlUO

-- Dumped from database version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: goods; Type: TABLE; Schema: public; Owner: kogotto
--

CREATE TABLE public.goods (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    is_active boolean DEFAULT true,
    username character varying(50) NOT NULL
);


ALTER TABLE public.goods OWNER TO kogotto;

--
-- Name: goods_id_seq; Type: SEQUENCE; Schema: public; Owner: kogotto
--

CREATE SEQUENCE public.goods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.goods_id_seq OWNER TO kogotto;

--
-- Name: goods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kogotto
--

ALTER SEQUENCE public.goods_id_seq OWNED BY public.goods.id;


--
-- Name: goods id; Type: DEFAULT; Schema: public; Owner: kogotto
--

ALTER TABLE ONLY public.goods ALTER COLUMN id SET DEFAULT nextval('public.goods_id_seq'::regclass);


--
-- Name: goods goods_pkey; Type: CONSTRAINT; Schema: public; Owner: kogotto
--

ALTER TABLE ONLY public.goods
    ADD CONSTRAINT goods_pkey PRIMARY KEY (id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT USAGE ON SCHEMA public TO kogo_list_bot;


--
-- Name: TABLE goods; Type: ACL; Schema: public; Owner: kogotto
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.goods TO kogo_list_bot;


--
-- Name: SEQUENCE goods_id_seq; Type: ACL; Schema: public; Owner: kogotto
--

GRANT ALL ON SEQUENCE public.goods_id_seq TO kogo_list_bot;


--
-- PostgreSQL database dump complete
--

\unrestrict UIJur83vYnmYhLCNTOUTE9koXxtSiKTw6on5U2z9gjSqgCISFRd0mIxU6BsGlUO

