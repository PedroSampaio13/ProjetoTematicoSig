<script>
    import Navbar from "$lib/components/Navbar.svelte";

    // Lista com os nomes dos criadores do projeto
    let criadores = [
        { nome: "Pedro Sampaio", numero: "119213" },
        { nome: "Ana Beatriz Vicente", numero: "114509" },
        { nome: "Tiago da Silva Coelho", numero: "109185" },
        { nome: "Guyvania Rosa", numero: "101515" },
        { nome: "Diogo Lemos", numero: "121286" },
        { nome: "Sara Presa", numero: "121354" },
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
        <h2 class="font-sora text-restaurante">Criadores</h2>
        <div class="creators-grid">
            {#each criadores as criador}
                <div class="creator-card bg-input">
                    <h3 class="font-sora">{criador.nome}</h3>
                    <p class="text-secondary">Número: {criador.numero}</p>
                </div>
            {/each}
        </div>
    </section>
</div>

<style>
    /* Contentor principal alinhado com o design do sistema */
    .about-container {
        max-width: 800px;
        margin: 0 auto;
        margin-top: var(--navbar-height);
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

    /* Grelha para a apresentação dos criadores */
    .creators-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-top: 20px;
    }

    .creator-card {
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
</style>
