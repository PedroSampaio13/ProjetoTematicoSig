<script>
    import Navbar from "$lib/components/Navbar.svelte";

    const desenvolvedores = [
        { nome: "Pedro Sampaio", numero: "119213", img: "/images/pedro.jpeg", color: "farmacia" },
        { nome: "Ana Beatriz Vicente", numero: "114509", img: "/images/ana.jpeg", color: "hospital" },
        { nome: "Tiago da Silva Coelho", numero: "109185", img: "/images/tiago.jpeg", color: "restaurante" },
        { nome: "Guyvania Rosa", numero: "101515", img: "/images/guyvania.svg", color: "farmacia" },
        { nome: "Diogo Lemos", numero: "121286", img: "/images/diogo.jpeg", color: "hospital" },
        { nome: "Sara Presa", numero: "121354", img: "/images/sara.jpeg", color: "restaurante" },
    ];

    const tecnologias = [
        { label: "SvelteKit", color: "farmacia" },
        { label: "OpenLayers", color: "hospital" },
        { label: "FastAPI", color: "restaurante" },
        { label: "PostgreSQL", color: "farmacia" },
        { label: "PostGIS", color: "hospital" },
        { label: "Redis", color: "restaurante" },
    ];

    const funcionalidades = [
        {
            titulo: "Pesquisa por categoria",
            descricao: "Filtra por farmácias, hospitais ou restaurantes e encontra rapidamente o que precisas.",
            color: "farmacia",
            icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
        },
        {
            titulo: "Visualização no mapa",
            descricao: "Vê todos os resultados num mapa interativo com marcadores codificados por categoria.",
            color: "hospital",
            icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
        },
        {
            titulo: "Routing a pé",
            descricao: "Calcula rotas a pé até qualquer local e obtém o tempo de chegada estimado.",
            color: "restaurante",
            icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="5" r="1"/><path d="M9 20l3-6 3 6"/><path d="M6 8l6 2 6-2"/><line x1="12" y1="10" x2="12" y2="14"/></svg>`,
        },
    ];

    const faqs = [
        { pergunta: "Como funciona a pesquisa no mapa?",
            resposta: "Permite encontrar farmácias, hospitais e restaurantes próximos e visualizá-los no mapa."},
        { pergunta: "Posso usar no telemóvel?",
            resposta: "A aplicação está otimizada para desktop." },
        { pergunta: "Preciso de conta?",
            resposta: "Não, a utilização é livre e não requer registo."}
    ];
</script>

<div class="about-container">
    <Navbar activeTab="sobre" />

    <header class="about-header">
        <h1 class="font-sora">Sobre o Projeto</h1>
        <p class="text-secondary">
            Conheça a nossa missão e a equipa por detrás do desenvolvimento.
        </p>
    </header>

    <section class="about-section bg-secondary shadow-md">
        <h2 class="font-sora text-farmacia">Enquadramento</h2>
        <p>
            O presente trabalho insere-se na unidade curricular Projeto de
            Sistemas de Informação Geográfica, e tem como âmbito o
            desenvolvimento de uma aplicação web de pesquisa de pontos de
            interesse no mapa, visando oferecer uma solução abrangente e
            conveniente para clientes.
        </p>
    </section>

    <section class="about-section bg-secondary shadow-md">
        <h2 class="font-sora text-hospital">Objetivos</h2>
        <p>
            O objetivo principal é facilitar a procura de serviços próximos:
            farmácias, hospitais e restaurantes, apresentando os
            resultados numa lista e permitindo a sua visualização direta no
            mapa.
        </p>
    </section>

    <section class="about-section bg-secondary shadow-md">
        <h2 class="font-sora text-restaurante">Funcionalidades</h2>
        <div class="features-grid">
            {#each funcionalidades as f}
                <div class="feature-card card-{f.color}">
                    <div class="feature-icon icon-{f.color}">
                        {@html f.icon}
                    </div>
                    <h3 class="feature-title">{f.titulo}</h3>
                    <p class="feature-desc">{f.descricao}</p>
                </div>
            {/each}
        </div>
    </section>

    <section class="about-section bg-secondary shadow-md">
        <h2 class="font-sora text-farmacia">Tecnologias Utilizadas</h2>
        <div class="tech-chips">
            {#each tecnologias as t}
                <span class="tech-chip chip-{t.color}">{t.label}</span>
            {/each}
        </div>
    </section>

    <section class="about-section bg-secondary shadow-md">
        <h2 class="font-sora text-restaurante">Desenvolvedores</h2>
        <div class="creators-grid">
            {#each desenvolvedores as d}
                <div class="creator-card card-{d.color}">
                    <img src={d.img} alt={d.nome} class="creator-img" loading="lazy" />
                    <div>
                        <h3 class="font-sora">{d.nome}</h3>
                        <p class="text-secondary">Nº {d.numero}</p>
                    </div>
                </div>
            {/each}
        </div>
    </section>

    <section class="about-section bg-secondary shadow-md">
        <h2 class="font-sora">Perguntas Frequentes</h2>
        {#each faqs as faq}
            <div class="faq-item">
                <h3>{faq.pergunta}</h3>
                <p>{faq.resposta}</p>
            </div>
        {/each}
    </section>
</div>

<style>
    .about-container {
        max-width: 800px;
        margin: 0 auto;
        margin-top: var(--navbar-height);
        margin-bottom: var(--navbar-height);
        height: 100%;
        overflow-y: auto;
        overflow-x: hidden;
        scrollbar-width: none;
        box-sizing: border-box;
    }

    .about-container::-webkit-scrollbar {
        display: none;
    }

    .about-header {
        text-align: center;
        margin-bottom: 40px;
    }

    .about-header h1 {
        font-size: 2.5rem;
        color: var(--text-primary);
        margin-bottom: 10px;
    }

    .about-section {
        margin: 50px 0;
        padding: 30px;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border);
        margin-bottom: 24px;
        transition:
            background-color var(--transition),
            border-color var(--transition);
    }

    .about-section h2 {
        font-size: 1.5rem;
        margin-bottom: 16px;
        font-weight: 600;
    }

    .about-section p {
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.6;
    }

    /* ── Cores temáticas ── */
    .text-farmacia    { color: var(--color-farmacia); }
    .text-hospital    { color: var(--color-hospital); }
    .text-restaurante { color: var(--color-restaurante); }
    .text-secondary   { color: var(--text-secondary); }
    .bg-secondary     { background-color: var(--bg-secondary); }
    .shadow-md        { box-shadow: var(--shadow-md); }

    /* ── Funcionalidades ── */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 14px;
        margin-top: 20px;
    }

    .feature-card {
        padding: 20px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        gap: 10px;
        transition: transform var(--transition);
    }

    .feature-card:hover {
        transform: translateY(-2px);
    }

    .feature-card.card-farmacia    { background: var(--color-farmacia-10);    border-color: color-mix(in srgb, var(--color-farmacia) 25%, transparent); }
    .feature-card.card-hospital    { background: var(--color-hospital-10);    border-color: color-mix(in srgb, var(--color-hospital) 25%, transparent); }
    .feature-card.card-restaurante { background: var(--color-restaurante-10); border-color: color-mix(in srgb, var(--color-restaurante) 25%, transparent); }

    .feature-icon {
        width: 44px;
        height: 44px;
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .feature-icon.icon-farmacia    { background: var(--color-farmacia-10);    color: var(--color-farmacia); }
    .feature-icon.icon-hospital    { background: var(--color-hospital-10);    color: var(--color-hospital); }
    .feature-icon.icon-restaurante { background: var(--color-restaurante-10); color: var(--color-restaurante); }

    .feature-title {
        font-family: 'Sora', sans-serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .feature-desc {
        font-size: 0.875rem;
        color: var(--text-secondary);
        line-height: 1.55;
        margin: 0;
    }

    /* ── Tecnologias ── */
    .tech-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
    }

    .tech-chip {
        padding: 6px 16px;
        border-radius: var(--radius-full);
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid transparent;
        transition: transform var(--transition);
    }

    .tech-chip:hover {
        transform: translateY(-1px);
    }

    .tech-chip.chip-farmacia    { background: var(--color-farmacia-10);    color: var(--color-farmacia);    border-color: color-mix(in srgb, var(--color-farmacia) 30%, transparent); }
    .tech-chip.chip-hospital    { background: var(--color-hospital-10);    color: var(--color-hospital);    border-color: color-mix(in srgb, var(--color-hospital) 30%, transparent); }
    .tech-chip.chip-restaurante { background: var(--color-restaurante-10); color: var(--color-restaurante); border-color: color-mix(in srgb, var(--color-restaurante) 30%, transparent); }

    /* ── Desenvolvedores ── */
    .creators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
        margin-top: 20px;
    }

    .creator-card {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 16px 20px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        transition: transform var(--transition);
    }

    .creator-card:hover {
        transform: translateY(-2px);
    }

    .creator-card.card-farmacia    { background: var(--color-farmacia-10);    border-left: 3px solid var(--color-farmacia); }
    .creator-card.card-hospital    { background: var(--color-hospital-10);    border-left: 3px solid var(--color-hospital); }
    .creator-card.card-restaurante { background: var(--color-restaurante-10); border-left: 3px solid var(--color-restaurante); }

    .creator-card h3 {
        font-size: 1rem;
        color: var(--text-primary);
        margin-bottom: 4px;
    }

    .creator-card p {
        font-size: 0.85rem;
        margin: 0;
    }

    .creator-card div {
        display: flex;
        flex-direction: column;
    }

    .creator-img {
        width: 52px;
        height: 52px;
        border-radius: 10%;
        object-fit: cover;
        border: 2px solid var(--border);
        flex-shrink: 0;
    }

    /* ── FAQ ── */
    .faq-item {
        padding: 15px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        background-color: var(--bg-input);
        margin-bottom: 10px;
    }

    .faq-item h3 {
        font-size: 0.95rem;
        color: var(--text-primary);
        margin-bottom: 6px;
    }

    .faq-item p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
    }
</style>
