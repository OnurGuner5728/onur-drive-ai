package com.onurdrive.diagnostics;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.SystemClock;
import android.util.Size;
import android.view.Surface;
import android.view.TextureView;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import java.util.Collections;

/** PARKED ONLY: explicit, read-only, public Camera2 preview; never OEM/vehicle control. */
public final class CameraProbeActivity extends Activity {
    private static final int CAMERA_PERMISSION_REQUEST = 32;
    private CameraManager manager;
    private Spinner cameraSelector;
    private TextureView texture;
    private TextView status;
    private CameraDevice device;
    private CameraCaptureSession session;
    private Surface surface;
    private HandlerThread cameraThread;
    private Handler cameraHandler;
    private String activeId = "";
    private boolean wanted = false;
    private long frames = 0;
    private long lastUpdate = 0;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setPadding(18,18,18,18);
        TextView heading = new TextView(this);
        heading.setText("ONUR DRIVE AI · GERÇEK KAMERA TESTİ");
        heading.setTextSize(19);
        layout.addView(heading);
        TextView notice = new TextView(this);
        notice.setText("SADECE PARK HALİNDE. Araç hız sınırı veya güvenlik sistemleri değiştirilmez. Yalnızca Android Camera2'nin izin verdiği kameralara erişim denenir.");
        layout.addView(notice);
        status = new TextView(this);
        status.setText("Camera2 kamerası taranıyor...");
        status.setTextIsSelectable(true);
        layout.addView(status);
        manager = (CameraManager)getSystemService(Context.CAMERA_SERVICE);
        cameraSelector = new Spinner(this);
        layout.addView(cameraSelector);
        Button start = new Button(this);
        start.setText("SEÇİLİ KAMERAYI AÇ (PARK)");
        layout.addView(start);
        Button stop = new Button(this);
        stop.setText("KAMERAYI KAPAT");
        layout.addView(stop);
        texture = new TextureView(this);
        layout.addView(texture,new LinearLayout.LayoutParams(-1,330));
        texture.setSurfaceTextureListener(new TextureView.SurfaceTextureListener() {
            @Override public void onSurfaceTextureAvailable(SurfaceTexture t,int w,int h) {
                if(wanted) open();
            }
            @Override public void onSurfaceTextureSizeChanged(SurfaceTexture t,int w,int h) {}
            @Override public boolean onSurfaceTextureDestroyed(SurfaceTexture t) {
                close();
                return true;
            }
            @Override public void onSurfaceTextureUpdated(SurfaceTexture t) {
                ++frames;
                long now = SystemClock.elapsedRealtime();
                if(now-lastUpdate>800) {
                    lastUpdate=now;
                    status.setText("Canlı gerçek kamera görüntüsü: ID "+activeId+" · kare "+frames+" (Camera2)");
                }
            }
        });
        setContentView(layout);
        try {
            String[] ids = manager.getCameraIdList();
            cameraSelector.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_dropdown_item,ids));
            status.setText(ids.length==0 ? "Camera2 aygıtı YOK. Fabrika AVM kamerası harici bir OEM arayüzünde olabilir."
                                        : ids.length+" Camera2 kamera bulundu. Liste fabrika kameralarının tamamını temsil etmeyebilir.");
            start.setEnabled(ids.length>0);
        } catch(Exception ex) {
            status.setText("Camera2 taraması başarısız: "+ex.getClass().getSimpleName());
            start.setEnabled(false);
        }
        start.setOnClickListener(v->start());
        stop.setOnClickListener(v->{
            close();
            status.setText("Kamera kapatıldı. Alınan kare: "+frames);
        });
    }

    private void start() {
        if(cameraSelector.getSelectedItem()==null) return;
        if(checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA},CAMERA_PERMISSION_REQUEST);
            return;
        }
        close();
        wanted=true;
        activeId=cameraSelector.getSelectedItem().toString();
        frames=0;
        status.setText("Kamera açılıyor: "+activeId);
        if(texture.isAvailable()) open();
    }

    @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] results) {
        super.onRequestPermissionsResult(request,permissions,results);
        if(request==CAMERA_PERMISSION_REQUEST) {
            if(results.length>0 && results[0]==PackageManager.PERMISSION_GRANTED) start();
            else status.setText("CAMERA izni yok: erişim denenmedi.");
        }
    }

    private void open() {
        if(!wanted || manager==null) return;
        try {
            CameraCharacteristics characteristics=manager.getCameraCharacteristics(activeId);
            StreamConfigurationMap configs=characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
            if(configs==null || configs.getOutputSizes(SurfaceTexture.class)==null) {
                status.setText("Camera2 akış yüzeyi sunulmuyor: "+activeId);
                return;
            }
            Size chosen=choose(configs.getOutputSizes(SurfaceTexture.class));
            SurfaceTexture t=texture.getSurfaceTexture();
            if(t==null) return;
            t.setDefaultBufferSize(chosen.getWidth(),chosen.getHeight());
            surface=new Surface(t);
            cameraThread=new HandlerThread("mg-camera-probe");
            cameraThread.start();
            cameraHandler=new Handler(cameraThread.getLooper());
            manager.openCamera(activeId,new CameraDevice.StateCallback() {
                @Override public void onOpened(CameraDevice opened) {
                    if(!wanted) {opened.close();return;}
                    device=opened;
                    try {
                        opened.createCaptureSession(Collections.singletonList(surface),new CameraCaptureSession.StateCallback() {
                            @Override public void onConfigured(CameraCaptureSession configured) {
                                if(!wanted) {configured.close();return;}
                                session=configured;
                                try {
                                    CaptureRequest.Builder request=opened.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
                                    request.addTarget(surface);
                                    configured.setRepeatingRequest(request.build(),null,cameraHandler);
                                    runOnUiThread(()->status.setText("Kamera açıldı. İlk canlı kare bekleniyor: "+activeId));
                                } catch(Exception ex) {error(ex);}
                            }
                            @Override public void onConfigureFailed(CameraCaptureSession session) {
                                error(new IllegalStateException("Capture session rejected"));
                            }
                        },cameraHandler);
                    } catch(Exception ex) {error(ex);}
                }
                @Override public void onDisconnected(CameraDevice disconnected) {
                    disconnected.close();
                    error(new IllegalStateException("Camera disconnected"));
                }
                @Override public void onError(CameraDevice failed,int code) {
                    failed.close();
                    error(new IllegalStateException("Camera2 error "+code));
                }
            },cameraHandler);
        } catch(Exception ex) {error(ex);}
    }

    private Size choose(Size[] sizes) {
        Size best=sizes[0];
        for(Size candidate:sizes) {
            if(candidate.getWidth()<=1280 && candidate.getHeight()<=720 &&
               (best.getWidth()>1280 || best.getHeight()>720 ||
               (long)candidate.getWidth()*candidate.getHeight()>(long)best.getWidth()*best.getHeight()))
                best=candidate;
        }
        return best;
    }

    private void error(Exception ex) {
        runOnUiThread(()->{
            status.setText("Kamera açılamadı: "+ex.getClass().getSimpleName()+". OEM izni veya Camera2 erişimi yok olabilir.");
            close();
        });
    }

    private void close() {
        wanted=false;
        try {if(session!=null){session.stopRepeating();session.close();}}catch(Exception ignored){}
        session=null;
        try {if(device!=null)device.close();}catch(Exception ignored){}
        device=null;
        if(surface!=null){surface.release();surface=null;}
        if(cameraThread!=null){cameraThread.quitSafely();cameraThread=null;}
        cameraHandler=null;
    }

    @Override protected void onPause() {
        close();
        super.onPause();
    }

    @Override protected void onDestroy() {
        close();
        super.onDestroy();
    }
}
