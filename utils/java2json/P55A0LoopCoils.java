import java.util.Arrays;
import java.util.Vector;

class P55A0LoopCoils extends PMCVariable {

    public P55A0LoopCoils() {
        super("MSA", "55 A0 loop coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    P55ADLoopCoils AD = new P55ADLoopCoils();
    P55AELoopCoils AE = new P55AELoopCoils();
}


