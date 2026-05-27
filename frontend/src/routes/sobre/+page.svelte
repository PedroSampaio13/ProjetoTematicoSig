<script>
    import Navbar from "$lib/components/Navbar.svelte";

    // Lista com os nomes dos desenvolvedores do projeto
    let desenvolvedores = [
        { nome: "Pedro Sampaio", numero: "119213", img: "/images/pedro.jpg" },
        { nome: "Ana Beatriz Vicente", numero: "114509", img: "/images/ana.jpg" },
        { nome: "Tiago da Silva Coelho", numero: "109185", img: "/images/tiago.jpg" },
        { nome: "Guyvania Rosa", numero: "101515", img: "/images/guyvania.jpg" },
        { nome: "Diogo Lemos", numero: "121286", img: "/images/diogo.jpg" },
        { nome: "Sara Presa", numero: "121354", img: "/images/sara.jpg" },
    ];

    let faqs = [
        { pergunta: "Como funciona a pesquisa no mapa?",
            resposta: "Permite encontrar farmácias, hospitais e restaurantes próximos e visualizá-los no mapa."},
        { pergunta: "Posso usar no telemóvel?",
            resposta: "Sim, a aplicação é responsiva e funciona em qualquer dispositivo." },
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
        <h2 class="font-sora text-restaurante">Desenvolvedores</h2>
        <div class="creators-grid">
            {#each desenvolvedores as d}
                <div class="creator-card bg-input">
                    <img src={d.img} alt={d.nome} class="creator-img" />
                    <div>
                        <h3 class="font-sora">{d.nome}</h3>
                        <p class="text-secondary">Número: {d.numero}</p>
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
    /* Contentor principal alinhado com o design do sistema */
    .about-container {
        max-width: 800px;
        margin: 0 auto;
        margin-top: var(--navbar-height);
        margin-bottom: var(--navbar-height);
        height: 100%;
        overflow-y: auto;
        box-sizing: border-box;
    }

    /* Estilização do cabeçalho */
    .about-header {
        text-align: center;
        margin-bottom: 40px;
    }

    .about-header h1 {
        font-size: 2.5rem;
        color: var(--text-primary);
        margin-bottom: 10px;
    }

    /* Estilização geral das secções */
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

    /* Cores temáticas baseadas nas variáveis fornecidas */
    .text-farmacia {
        color: var(--color-farmacia);
    }

    .text-hospital {
        color: var(--color-hospital);
    }

    .text-restaurante {
        color: var(--color-restaurante);
    }

    /* Helpers de texto do próprio CSS base */
    .text-secondary {
        color: var(--text-secondary);
    }

    .bg-secondary {
        background-color: var(--bg-secondary);
    }

    .bg-input {
        background-color: var(--bg-input);
    }

    /* Sombras dinâmicas */
    .shadow-md {
        box-shadow: var(--shadow-md);
    }

    /* Grelha para a apresentação dos desenvolvedores */
    .creators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-top: 20px;
        align-items: center;
        gap: 12px;

    }

    .creator-card {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 20px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        transition: transform var(--transition);
    }

    .creator-card:hover {
        transform: translateY(-2px);
    }

    .creator-card h3 {
        font-size: 1.15rem;
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
        width: 60px;
        height: 60px;
        border-radius: 10%;
        object-fit: cover;
        border: 2px solid var(--border);
    }

    .faq-item {
        padding: 15px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        background-color: var(--bg-input);
        margin-bottom: 10px;
    }
</style>
