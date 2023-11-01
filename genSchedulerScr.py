#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !DESCRIPTION:
#
# !CALLING SEQUENCE:
#
# !REVISION HISTORY: 
# 26 out 2023 - J. G. de Mattos - Initial Version
#
# !REMARKS:
#
#EOP
#-----------------------------------------------------------------------------#
#BOC
from genScheduler.script_generator import read_yaml_config, generate_submission_script, parser

def main():
    
    args   = parser()
    config = read_yaml_config('config.yml')
    script = generate_submission_script(config, args)


    with open(f'{args.scheduler}_submission_script.sh', 'w') as script_file:
        script_file.write(script)

if __name__ == '__main__':
    
    main()


#EOC
#-----------------------------------------------------------------------------#

