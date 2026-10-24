package com.agesofdominion.game;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.JsResult;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.window.OnBackInvokedDispatcher;

import androidx.webkit.WebViewAssetLoader;

public class MainActivity extends Activity {
    private WebView web;
    private int lifecycleGeneration;
    private ValueCallback<Uri[]> fileChooserCallback;
    private static final int REQUEST_FILE_CHOOSER = 1001;
    private volatile boolean canHandleBack = false;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    private Runnable pendingAfter;
    private Runnable saveWaiter;
    private int saveGeneration;
    private String lastSaveStatus = "none";
    private String lastCommittedHead = "null";

    public class SaveBridge {
        @JavascriptInterface
        public void ack(String token, String status, String committedHead) {
            mainHandler.post(() -> {
                if (!Integer.toString(saveGeneration).equals(token)) return;
                lastCommittedHead = committedHead;
                finishBackground(status);
            });
        }
    }

    public class BackBridge {
        @JavascriptInterface
        public void setBackActive(boolean active) {
            canHandleBack = active;
        }
    }

    private void hideSystemUI() {
        try {
            View decor = getWindow().peekDecorView();
            if (decor == null) return;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                WindowInsetsController controller = decor.getWindowInsetsController();
                if (controller != null) {
                    controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                    controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
                }
            } else {
                decor.setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                );
            }
        } catch (Throwable ignored) {}
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
                OnBackInvokedDispatcher.PRIORITY_DEFAULT,
                () -> {
                    if (canHandleBack && web != null) {
                        web.evaluateJavascript("if (window.rebornHandleBack) window.rebornHandleBack();", null);
                    } else {
                        finish();
                    }
                }
            );
        }

        WebViewAssetLoader assets = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();
        web = new WebView(this);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.addJavascriptInterface(new BackBridge(), "rebornNativeBridge");
        web.addJavascriptInterface(new SaveBridge(), "RebornSave");
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return assets.shouldInterceptRequest(request.getUrl());
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
                new AlertDialog.Builder(MainActivity.this)
                        .setTitle("Confirmation")
                        .setMessage(message)
                        .setPositiveButton(android.R.string.ok, (dialog, which) -> result.confirm())
                        .setNegativeButton(android.R.string.cancel, (dialog, which) -> result.cancel())
                        .setOnCancelListener(dialog -> result.cancel())
                        .show();
                return true;
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                if (fileChooserCallback != null) {
                    fileChooserCallback.onReceiveValue(null);
                }
                fileChooserCallback = filePathCallback;
                Intent intent = fileChooserParams.createIntent();
                try {
                    startActivityForResult(intent, REQUEST_FILE_CHOOSER);
                } catch (Exception e) {
                    fileChooserCallback = null;
                    return false;
                }
                return true;
            }
        });
        setContentView(web);
        hideSystemUI();
        web.loadUrl("https://appassets.androidplatform.net/assets/www/index.html");
    }

    @Override
    public void onBackPressed() {
        if (canHandleBack && web != null) {
            web.evaluateJavascript("if (window.rebornHandleBack) window.rebornHandleBack();", null);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            hideSystemUI();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQUEST_FILE_CHOOSER) {
            if (fileChooserCallback != null) {
                Uri[] results = null;
                if (resultCode == Activity.RESULT_OK && data != null) {
                    Uri uri = data.getData();
                    if (uri != null) {
                        results = new Uri[]{uri};
                    } else if (data.getClipData() != null) {
                        int count = data.getClipData().getItemCount();
                        results = new Uri[count];
                        for (int i = 0; i < count; i++) {
                            results[i] = data.getClipData().getItemAt(i).getUri();
                        }
                    }
                }
                fileChooserCallback.onReceiveValue(results);
                fileChooserCallback = null;
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    private void finishBackground(String status) {
        lastSaveStatus = status;
        if (saveWaiter != null) {
            mainHandler.removeCallbacks(saveWaiter);
            saveWaiter = null;
        }
        Runnable after = pendingAfter;
        pendingAfter = null;
        if (after != null) after.run();
    }

    private void background(boolean hidden, Runnable after) {
        if (web == null) {
            if (after != null) after.run();
            return;
        }
        pendingAfter = after;
        final int requestGeneration = ++saveGeneration;
        final String token = Integer.toString(requestGeneration);
        if (saveWaiter != null) mainHandler.removeCallbacks(saveWaiter);
        saveWaiter = () -> {
            if (requestGeneration == saveGeneration) finishBackground("timeout");
        };
        mainHandler.postDelayed(saveWaiter, 2500);
        String script = "(function(){var token='" + token + "';if(!window.rebornBackground){if(window.RebornSave)window.RebornSave.ack(token,'missing','null');return 'missing';}"
                + "var result=window.rebornBackground(" + hidden + ");"
                + "var finish=function(ok){var receipt=window.rebornCommittedHead?window.rebornCommittedHead():null;if(window.RebornSave)window.RebornSave.ack(token,ok?'saved':'failed',JSON.stringify(receipt));};"
                + "if(result&&typeof result.then==='function'){result.then(function(ok){finish(ok!==false);},function(){finish(false);});return 'pending';}"
                + "finish(result!==false);return result?'saved':'failed';})()";
        web.evaluateJavascript(script, null);
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
        hideSystemUI();
        background(false, null);
    }
}
