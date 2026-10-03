package com.agesofdominion.game;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setAllowFileAccess(true);
        setContentView(web);
        web.loadUrl("file:///android_asset/www/index.html");
    }
}
