package com.onurdrive.diagnostics;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Typeface;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.os.Build;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.content.Context;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import org.json.JSONObject;
import org.json.JSONArray;

/** Read-only head-unit inventory and Turkish TTS verification. No camera capture. */
public final class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private static final int SAVE_DIAGNOSTICS = 403;
    private TextToSpeech tts;
    private boolean ttsReady = false;
    private String report = "{}";
    private TextView body;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setPadding(24, 24, 24, 24);
        column.setBackgroundColor(0xff0b1627);
        TextView title = new TextView(this);
        title.setText("ONUR DRIVE AI · TANILAMA");
        title.setTextSize(23);
        title.setTypeface(null,Typeface.BOLD);
        title.setTextColor(0xff4ce3cf);
        column.addView(title);
        TextView disclaimer = new TextView(this);
        disclaimer.setText("Salt okunur envanter. OEM kamera akışı açılmaz, hız sınırı değiştirilmez, araca kontrol komutu gönderilmez.");
        disclaimer.setTextColor(0xffffce79);
        disclaimer.setTextSize(15);
        disclaimer.setPadding(0,15,0,20);
        column.addView(disclaimer);
        Button camera = makeButton("FABRİKA KAMERASI ERİŞİMİNİ TEST ET (PARK)", column);
        Button scan = makeButton("Sistemi yeniden tara", column);
        Button voice = makeButton("Türkçe ses testi", column);
        Button save = makeButton("Tanı raporunu kaydet", column);
        Button coffee = makeButton("Bir kahve ısmarla · Patreon (isteğe bağlı)", column);
        body = new TextView(this);
        body.setTextColor(0xffd8e8f6);
        body.setTextSize(14);
        body.setTextIsSelectable(true);
        body.setPadding(0,20,0,20);
        ScrollView scroll = new ScrollView(this);
        scroll.addView(body);
        column.addView(scroll);
        setContentView(column);
        scan.setOnClickListener(v -> scan());
        voice.setOnClickListener(v -> speak());
        save.setOnClickListener(v -> save());
        camera.setOnClickListener(v -> startActivity(new Intent(this, CameraProbeActivity.class)));
        coffee.setOnClickListener(v -> startActivity(new Intent(Intent.ACTION_VIEW, android.net.Uri.parse("https://www.patreon.com/c/onurguner"))));
        tts=new TextToSpeech(this,this);
        scan();
    }

    private Button makeButton(String text, LinearLayout group) {
        Button b = new Button(this);
        b.setText(text); group.addView(b);return b;
    }

    private void scan() {
        JSONObject root = new JSONObject();
        StringBuilder screen=new StringBuilder();
        try {
            root.put("purpose","READ_ONLY_DIAGNOSTICS");
            root.put("os_release",Build.VERSION.RELEASE);
            root.put("sdk",Build.VERSION.SDK_INT);
            root.put("manufacturer",Build.MANUFACTURER);
            root.put("model",Build.MODEL);
            root.put("hardware",Build.HARDWARE);
            root.put("car_control","NOT_IMPLEMENTED");
            root.put("raw_oem_camera_access","UNVERIFIED");
            root.put("adb_enabled","NOT_TESTED");
            JSONArray cams = new JSONArray();
            try {
                CameraManager manager=(CameraManager)getSystemService(Context.CAMERA_SERVICE);
                String[] ids=manager.getCameraIdList();
                for (String id: ids) {
                    JSONObject cam = new JSONObject();
                    cam.put("id",id);
                    try {
                        CameraCharacteristics c=manager.getCameraCharacteristics(id);
                        Integer facing=c.get(CameraCharacteristics.LENS_FACING);
                        cam.put("lens_facing",facing == null ? "unknown" : facing);
                        cam.put("hardware_level",c.get(CameraCharacteristics.INFO_SUPPORTED_HARDWARE_LEVEL));
                    } catch (Exception ex) { cam.put("detail_error",ex.getClass().getSimpleName()); }
                    cams.put(cam);
                }
                root.put("camera2_enumerated",true);
            } catch (Exception ex) {
                root.put("camera2_enumerated",false);
                root.put("camera2_error",ex.getClass().getSimpleName());
            }
            root.put("camera2_devices",cams);
            // Note: Camera2 devices are not a complete enumeration of OEM cameras.
            root.put("important_note","OEM AVM cameras may be hidden from the public Camera2 API. No camera stream requested.");
            report=root.toString(2);
            screen.append(report);
        } catch(Exception ex) {screen.append("Error: ").append(ex.getClass().getSimpleName());}
        body.setText(screen.toString());
    }

    @Override public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS && tts!=null) {
            int language=tts.setLanguage(new Locale("tr","TR"));
            ttsReady = language != TextToSpeech.LANG_MISSING_DATA && language != TextToSpeech.LANG_NOT_SUPPORTED;
        }
    }

    private void speak() {
        if (!ttsReady) {
            body.append("\n\nTürkçe TTS desteklenmiyor veya ses paketi yüklü değil.");
            return;
        }
        tts.speak("Bu bir Türkçe ses testidir. Araç kontrolü kapalıdır.",TextToSpeech.QUEUE_FLUSH,null,"demo");
    }

    private void save() {
        Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/json");
        i.putExtra(Intent.EXTRA_TITLE,"mg_hs_onur_drive_probe.json");
        startActivityForResult(i,SAVE_DIAGNOSTICS);
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        if (requestCode==SAVE_DIAGNOSTICS && resultCode==RESULT_OK && data!=null && data.getData()!=null) {
            try (OutputStream os=getContentResolver().openOutputStream(data.getData())) {
                if (os!=null) os.write(report.getBytes(StandardCharsets.UTF_8));
            } catch(Exception ex) {body.append("\nKaydetme hatası: "+ex.getClass().getSimpleName());}
        }
    }
    @Override protected void onDestroy() {if (tts != null) tts.shutdown();super.onDestroy();}
}
