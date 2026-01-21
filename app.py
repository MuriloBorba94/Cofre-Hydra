import streamlit as st
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="HYDRA COFRE v1.0", page_icon="🐉", layout="wide")

# --- ESTILIZAÇÃO ULTRA MODERNIZADA ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
       
        :root {
            --primary: #ff0090;
            --primary-glow: rgba(255, 0, 144, 0.4);
            --bg: #020202;
            --card-bg: rgba(18, 18, 18, 0.7);
            --border: rgba(255, 255, 255, 0.08);
        }
        .stApp {
            background-color: var(--bg);
            background-image:
                radial-gradient(circle at 10% 10%, rgba(255, 0, 144, 0.08) 0%, transparent 30%),
                radial-gradient(circle at 90% 90%, rgba(0, 212, 255, 0.05) 0%, transparent 30%);
            color: #ffffff;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] { visibility: hidden; }
        /* Typography */
        h1, h2, h3 {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800 !important;
            letter-spacing: -1px;
        }
        /* Glass Cards */
        .hydra-card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 28px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .hydra-card:hover {
            border-color: rgba(255, 0, 144, 0.3);
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        /* Neon Buttons */
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, var(--primary) 0%, #9d0059 100%) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 18px !important;
            padding: 14px 28px !important;
            font-size: 14px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s !important;
            box-shadow: 0 8px 16px rgba(255, 0, 144, 0.2) !important;
        }
        .stButton>button:hover {
            box-shadow: 0 12px 24px var(--primary-glow) !important;
            transform: scale(1.02);
        }
        /* Metrics */
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.03);
            padding: 20px;
            border-radius: 20px;
            border: 1px solid var(--border);
        }
        div[data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 1.8rem !important;
            background: linear-gradient(to right, #fff, #888);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        /* Inputs */
        div[data-baseweb="input"] {
            background-color: rgba(0,0,0,0.2) !important;
            border-radius: 14px !important;
            border: 1px solid var(--border) !important;
        }
       
        .magenta-glow {
            color: var(--primary);
            text-shadow: 0 0 20px var(--primary-glow);
        }
        .transaction-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
       
        /* Hide scrollbar */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String, unique=True)
    password = sa.Column(sa.String)
    role = sa.Column(sa.String)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = sa.Column(sa.Integer, primary_key=True)
    family = sa.Column(sa.String)
    dirty_amount = sa.Column(sa.Float)
    returned_amount = sa.Column(sa.Float)
    profit = sa.Column(sa.Float)
    category = sa.Column(sa.String)
    bleach_count = sa.Column(sa.Integer)
    created_by = sa.Column(sa.String)
    timestamp = sa.Column(sa.DateTime, default=datetime.now)

class Setting(Base):
    __tablename__ = 'settings'
    key = sa.Column(sa.String, primary_key=True)
    value = sa.Column(sa.Float)

engine = sa.create_engine('sqlite:///hydra.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db = Session()

def init_db():
    if not db.query(Setting).filter_by(key="taxPista").first():
        db.add_all([
            Setting(key="taxPista", value=45.0),
            Setting(key="taxProdutos", value=40.0),
            Setting(key="bleachPrice", value=8000.0),
            Setting(key="machineTax", value=30.0)
        ])
    if not db.query(User).filter_by(username="admin").first():
        db.add(User(username="admin", password="hydra123", role="LIDER"))
    db.commit()

init_db()

# --- SESSÃO ---
if 'user' not in st.session_state:
    st.session_state.user = None

def get_settings():
    return {s.key: s.value for s in db.query(Setting).all()}

# --- TELA DE LOGIN (MINIMALISTA E MODERNA) ---
if st.session_state.user is None:
    st.markdown('<div style="height: 15vh"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.2, 1.5, 1.2])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 40px;">
                <img src="https://media.discordapp.net/attachments/1111490812069564436/1462884504803741839/image.png?ex=6970799d&is=696f281d&hm=74cf59715d4bfacc714f84212886159efa41072063f6c8d11422809d36327bea&=&format=webp&quality=lossless"
                     style="width: 100px; filter: drop-shadow(0 0 20px var(--primary-glow)); border-radius: 50%; margin-bottom: 20px;">
                <h1 style="font-size: 2.8rem; margin:0;">HYDRA <span class="magenta-glow">FINANCES™</span></h1>
                <p style="color: #444; font-family: 'JetBrains Mono'; font-size: 12px; letter-spacing: 4px;">SECURYT LOGIN SYSTEM</p>
            </div>
        """, unsafe_allow_html=True)
       
        with st.container():
            u_in = st.text_input("IDENTIFIER")
            p_in = st.text_input("ACCESS KEY", type="password")
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            if st.form_submit_button if False else st.button("INITIALIZE SESSION"):
                found = db.query(User).filter_by(username=u_in, password=p_in).first()
                if found:
                    st.session_state.user = {"username": found.username, "role": found.role}
                    st.rerun()
                else:
                    st.toast("Access Denied: Invalid Credentials", icon="❌")
            st.markdown('</div>', unsafe_allow_html=True)

# --- DASHBOARD PRINCIPAL ---
else:
    user = st.session_state.user
    conf = get_settings()
   
    # Top Navbar Flutuante
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 15px 30px; background: rgba(255,255,255,0.02); border-radius: 20px; border: 1px solid var(--border); margin-bottom: 30px;">
            <div>
                <h2 style="margin:0; font-size: 1.5rem;">HYDRA <span class="magenta-glow">FINANCES</span> <small style="font-size: 10px; opacity:0.3; vertical-align: middle;">V1.0</small></h2>
                <p style="margin:0; font-size: 12px; opacity:0.6;">Sessão ativa: <span style="color:#fff; font-weight:600;">{user['username'].upper()}</span> | <span class="magenta-glow">{user['role']}</span></p>
            </div>
            <div style="display: flex; gap: 10px;">
                <span style="padding: 6px 15px; background: rgba(16, 185, 129, 0.1); color: #10b981; border-radius: 30px; font-size: 11px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.2);">SYSTEM ONLINE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    

    # Seletor de Data para Histórico
    selected_date = st.date_input("Selecionar Data para Histórico", value=datetime.today())

    # Grid de Conteúdo
    col_input, col_stats = st.columns([1, 2.2])
    with col_input:
        st.markdown("<p style='font-size: 22px; font-weight: 800; color: #666666; letter-spacing: 2px; text-transform: uppercase;'>Terminal de Lavagem</p>", unsafe_allow_html=True)
       
        with st.form("lavagem_ultra", clear_on_submit=True):
            f_client = st.text_input("ORG / CLIENTE", placeholder="Ex: Vagos")
            f_amount = st.number_input("QUANTIA SUJA (R$)", min_value=0.0, step=50000.0)
           
            sug = int((f_amount / 1000000) * 5) if f_amount > 0 else 0
            f_bleach = st.number_input(f"ALVEJANTES", min_value=0, value=sug)
           
            f_cat = st.radio("MODO", ["Pista", "Produtos"], horizontal=True)
           
            st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
            if st.form_submit_button("PROCESSAR TRANSAÇÃO"):
                if f_client and f_amount > 0:
                    tax = conf['taxPista'] if f_cat == "Pista" else conf['taxProdutos']
                    ret = f_amount * (1 - (tax / 100))
                    mach = f_amount * (conf['machineTax'] / 100)
                    cst = f_bleach * conf['bleachPrice']
                    prof = f_amount - ret - mach - cst
                   
                    db.add(Transaction(
                        family=f_client, dirty_amount=f_amount, returned_amount=ret,
                        profit=prof, category=f_cat, bleach_count=f_bleach,
                        created_by=user['username']
                    ))
                    db.commit()
                    st.toast(f"Transação {f_client} registrada!", icon="✅")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
       
        if st.button("ENCERRAR TERMINAL"):
            st.session_state.user = None
            st.rerun()
    with col_stats:
        # Mini Dash de Métricas (baseado na data selecionada)
        all_t = db.query(Transaction).filter(sa.func.date(Transaction.timestamp) == selected_date).all()
        t_dirty = sum(x.dirty_amount for x in all_t)
        t_prof = sum(x.profit for x in all_t)
        t_ret = sum(x.returned_amount for x in all_t)
        m1, m2, m3 = st.columns(3)
        m1.metric("VOLUME BRUTO", f"R$ {t_dirty:,.0f}")
        m2.metric("FLUXO DE CAIXA", f"R$ {t_ret:,.0f}")
        m3.metric("LUCRO HYDRA", f"R$ {t_prof:,.0f}")
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
       
        # Lista de Transações High-Tech (filtrado pela data selecionada)
        st.markdown("<p style='font-size: 11px; font-weight: 800; color: #666; letter-spacing: 2px; text-transform: uppercase;'>Logs de Atividade Recente</p>", unsafe_allow_html=True)
       
        recentes = db.query(Transaction).filter(sa.func.date(Transaction.timestamp) == selected_date).order_by(Transaction.timestamp.desc()).all()
       
        if not recentes:
            st.markdown('<div class="hydra-card" style="text-align:center; padding: 40px; opacity:0.5;">AGUARDANDO INGESTÃO DE DADOS...</div>', unsafe_allow_html=True)
        else:
            for r in recentes:
                accent = "#ff0090" if r.category == "Pista" else "#00d4ff"
                st.markdown(f"""
                <div class="hydra-card" style="padding: 18px; margin-bottom: 12px; border-left: 2px solid {accent}; background: rgba(255,255,255,0.01);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-family: 'JetBrains Mono'; font-weight: 700; font-size: 1.1rem;">{r.family.upper()}</span>
                            <span style="margin-left: 10px; font-size: 9px; padding: 2px 8px; border-radius: 4px; background: {accent}22; color: {accent}; border: 1px solid {accent}44;">{r.category.upper()}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 13px; font-weight: 800; color: #10b981;">+ R$ {r.profit:,.2f}</span><br>
                            <span style="font-size: 9px; opacity: 0.4;">{r.timestamp.strftime('%H:%M:%S')}</span>
                        </div>
                    </div>
                    <div style="margin-top: 12px; display: flex; gap: 20px; opacity: 0.7; font-size: 11px;">
                        <span><b style="color:#888">BRUTO:</b> R$ {r.dirty_amount:,.0f}</span>
                        <span><b style="color:#888">ALVEJANTES:</b> {r.bleach_count}</span>
                        <span style="margin-left: auto;">OPERADOR: <b style="color:{accent}">{r.created_by.upper()}</b></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Botões de Ação (Apenas para quem criou ou Líder)
                if user['role'] == 'LIDER' or user['username'] == r.created_by:
                    c_act1, c_act2, c_act3 = st.columns([1, 1, 4])
                   
                    with c_act1:
                        with st.popover("✏️"):
                            st.markdown("### Editar Registro")
                            with st.form(f"edit_{r.id}"):
                                new_family = st.text_input("Família", value=r.family)
                                new_dirty = st.number_input("Valor Sujo", value=r.dirty_amount)
                                new_bleach = st.number_input("Alvejantes", value=r.bleach_count)
                                if st.form_submit_button("SALVAR ALTERAÇÕES"):
                                    tax = conf['taxPista'] if r.category == "Pista" else conf['taxProdutos']
                                    ret = new_dirty * (1 - (tax / 100))
                                    mach = new_dirty * (conf['machineTax'] / 100)
                                    cst = new_bleach * conf['bleachPrice']
                                    prof = new_dirty - ret - mach - cst
                                   
                                    db.query(Transaction).filter_by(id=r.id).update({
                                        "family": new_family, "dirty_amount": new_dirty,
                                        "bleach_count": new_bleach, "returned_amount": ret, "profit": prof
                                    })
                                    db.commit()
                                    st.success("Atualizado!")
                                    st.rerun()
                   
                    with c_act2:
                        if st.button("🗑️", key=f"del_{r.id}"):
                            db.query(Transaction).filter_by(id=r.id).delete()
                            db.commit()
                            st.toast("Registro removido", icon="🗑️")
                            st.rerun()
    # Footer Administrativo
    if user['role'] == "LIDER":
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        with st.expander("🛠️ NÚCLEO DE COMANDO (ACESSO LÍDER)"):
            c1, c2 = st.tabs(["RECALIBRAGEM DE TAXAS", "GESTÃO DE OPERADORES"])
            with c1:
                st.markdown('<div style="padding: 20px;">', unsafe_allow_html=True)
                ca, cb = st.columns(2)
                np = ca.number_input("TAXA PISTA (%)", value=conf['taxPista'])
                nb = ca.number_input("CUSTO ALVEJANTE (R$)", value=conf['bleachPrice'])
                no = cb.number_input("TAXA PRODUTOS (%)", value=conf['taxProdutos'])
                nm = cb.number_input("TAXA MÁQUINA (%)", value=conf['machineTax'])
                if st.button("EFETUAR OVERWRITE DE PARÂMETROS"):
                    db.query(Setting).filter_by(key="taxPista").update({"value": np})
                    db.query(Setting).filter_by(key="taxProdutos").update({"value": no})
                    db.query(Setting).filter_by(key="bleachPrice").update({"value": nb})
                    db.query(Setting).filter_by(key="machineTax").update({"value": nm})
                    db.commit()
                    st.success("Sincronização completa.")
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div style="padding: 20px;">', unsafe_allow_html=True)
                with st.form("new_agent"):
                    an = st.text_input("NOME DO AGENTE")
                    ak = st.text_input("SENHA CRIPTOGRAFADA")
                    ar = st.selectbox("HIERARQUIA", ["GERENTE", "LIDER"])
                    if st.form_submit_button("RECRUTAR AGENTE"):
                        if an and ak:
                            try:
                                db.add(User(username=an, password=ak, role=ar))
                                db.commit()
                                st.success("Agente integrado ao sistema.")
                            except: st.error("Erro fatal: Agente já existente.")
                
                # Lista de Usuários com Opção de Deletar
                st.markdown("<p style='font-size: 14px; font-weight: 600; margin-top: 30px;'>Agentes Ativos</p>", unsafe_allow_html=True)
                users = db.query(User).all()
                for u in users:
                    if u.username != "admin" and u.username != user['username']:  # Não deletar admin ou si mesmo
                        col_u1, col_u2 = st.columns([3, 1])
                        with col_u1:
                            st.write(f"{u.username.upper()} ({u.role})")
                        with col_u2:
                            if st.button("EXTERMINAR", key=f"del_user_{u.id}"):
                                db.query(User).filter_by(id=u.id).delete()
                                db.commit()
                                st.toast("Agente eliminado do sistema.", icon="🗑️")
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 40px; opacity: 0.2; font-family: 'JetBrains Mono'; font-size: 10px; letter-spacing: 10px;">
            HYDRA COFRE v1.0 // METROPOLE SECTOR 7 // END-TO-END ENCRYPTION
        </div>
    """, unsafe_allow_html=True)
