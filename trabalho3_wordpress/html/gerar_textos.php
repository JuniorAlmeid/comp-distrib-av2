<?php
// Carrega o núcleo do WordPress para podermos usar as funções dele
require_once('wp-load.php');

// Slugs (URLs) que você já configurou no Locust e o tamanho desejado em bytes
$cenarios = [
    'post-imagem-300kb' => 300 * 1024,   // 300 KB
    'post-texto-400k'   => 400 * 1024,   // 400 KB
    'post-imagem-1mb'   => 1024 * 1024   // 1 MB
];

echo "<h2>Injetando textos nos posts...</h2>";

foreach ($cenarios as $slug => $tamanho_bytes) {
    // Cria um bloco de texto contínuo até atingir o tamanho exato
    $texto_base = "Teste de carga Locust. ";
    $repeticoes = ceil($tamanho_bytes / strlen($texto_base));
    $conteudo_exato = substr(str_repeat($texto_base, $repeticoes), 0, $tamanho_bytes);

    // Procura se o post com essa URL já existe
    $args = array('name' => $slug, 'post_type' => 'post', 'numberposts' => 1);
    $posts_encontrados = get_posts($args);

    if ($posts_encontrados) {
        // Se o post existe, atualiza ele trocando a foto pelo texto gigante
        $post_id = $posts_encontrados[0]->ID;
        wp_update_post(array(
            'ID'           => $post_id,
            'post_content' => $conteudo_exato
        ));
        echo "<p>✅ Post <b>{$slug}</b> atualizado para " . ($tamanho_bytes/1024) . "KB de texto puro.</p>";
    } else {
        // Se você apagou o post sem querer, ele recria com a mesma URL
        wp_insert_post(array(
            'post_title'   => 'Cenario ' . ($tamanho_bytes/1024) . 'KB',
            'post_name'    => $slug,
            'post_content' => $conteudo_exato,
            'post_status'  => 'publish',
            'post_author'  => 1
        ));
        echo "<p>➕ Post <b>{$slug}</b> CRIADO com " . ($tamanho_bytes/1024) . "KB de texto puro.</p>";
    }
}

echo "<h3>🎉 Tudo pronto! O banco de dados foi atualizado. Pode rodar seus testes!</h3>";
?>