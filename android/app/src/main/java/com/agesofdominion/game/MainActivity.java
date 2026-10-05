package com.agesofdominion.game;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {
    private WebView web;
    private int lifecycleGeneration;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebViewAssetLoader assets = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();
        web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assets.shouldInterceptRequest(request.getUrl());
            }
        });
        setContentView(web);
        web.loadUrl("https://appassets.androidplatform.net/assets/www/index.html");
    }

    private void background(boolean hidden, Runnable after) {
        if (web == null) {
            if (after != null) after.run();
            return;
        }
        String script = "(function(){if(window.rebornBackground){window.rebornBackground("
                + hidden + ");return 'saved';}return 'missing';})()";
        web.evaluateJavascript(script, value -> {
            if (after != null) after.run();
        });
    }

    @Override
    protected void onPause() {
        int token = ++lifecycleGeneration;
        background(true, () -> {
            if (token == lifecycleGeneration && web != null) web.onPause();
        });
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        lifecycleGeneration++;
        if (web != null) web.onResume();
        background(false, null);
    }
}
